#!/bin/bash
# =============================================================================
# setup.sh - 新しいMacをHomebrew中心でセットアップするスクリプト
#
# 使い方:
#   ./setup.sh            通常実行（対話的に各フェーズを確認）
#   ./setup.sh --dry-run  実際のインストールは行わず、実行内容を表示
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BREWFILE_PATH="${SCRIPT_DIR}/Brewfile"
LOG_FILE="${SCRIPT_DIR}/setup.log"
DRY_RUN=false

# 引数解析
for arg in "$@"; do
    case "${arg}" in
        --dry-run) DRY_RUN=true ;;
        *) echo "Unknown option: ${arg}"; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# ユーティリティ関数
# ---------------------------------------------------------------------------
info()    { echo -e "\033[1;34m[INFO]\033[0m $*" | tee -a "${LOG_FILE}"; }
warn()    { echo -e "\033[1;33m[WARN]\033[0m $*" | tee -a "${LOG_FILE}"; }
error()   { echo -e "\033[1;31m[ERROR]\033[0m $*" | tee -a "${LOG_FILE}"; }
success() { echo -e "\033[1;32m[OK]\033[0m $*" | tee -a "${LOG_FILE}"; }
dry()     { echo -e "\033[1;35m[DRY-RUN]\033[0m $*"; }

# 確認プロンプト（dry-run時はスキップ）
confirm() {
    if "${DRY_RUN}"; then return 0; fi
    local message="$1"
    read -rp "${message} (y/N): " answer
    [[ "${answer}" =~ ^[Yy]$ ]]
}

# コマンド実行（dry-run対応）
run() {
    if "${DRY_RUN}"; then
        dry "実行予定: $*"
    else
        "$@"
    fi
}

# ---------------------------------------------------------------------------
# Phase 1: システム情報の確認
# ---------------------------------------------------------------------------
phase_system_check() {
    info "===== Phase 1: システム情報の確認 ====="

    local arch
    arch=$(uname -m)
    local os_version
    os_version=$(sw_vers -productVersion)
    local hostname
    hostname=$(hostname)

    info "ホスト名:   ${hostname}"
    info "macOS:      ${os_version}"
    info "アーキテクチャ: ${arch}"

    if [[ "${arch}" == "arm64" ]]; then
        success "Apple シリコンを検出しました"
        HOMEBREW_PREFIX="/opt/homebrew"
    else
        info "Intel Mac を検出しました"
        HOMEBREW_PREFIX="/usr/local"
    fi

    # Brewfile の存在確認
    if [[ ! -f "${BREWFILE_PATH}" ]]; then
        error "Brewfile が見つかりません: ${BREWFILE_PATH}"
        error "先に旧Macで export.sh を実行して Brewfile を生成してください"
        exit 1
    fi
    success "Brewfile を検出しました: ${BREWFILE_PATH}"

    echo ""
}

# ---------------------------------------------------------------------------
# Phase 2: Xcode Command Line Tools
# ---------------------------------------------------------------------------
phase_xcode_clt() {
    info "===== Phase 2: Xcode Command Line Tools ====="

    if xcode-select -p &>/dev/null; then
        success "Xcode Command Line Tools はインストール済みです"
    else
        if confirm "Xcode Command Line Tools をインストールしますか？"; then
            info "Xcode Command Line Tools をインストールしています..."
            run xcode-select --install
            if ! "${DRY_RUN}"; then
                info "インストールダイアログが表示されたら、指示に従ってください"
                info "インストールが完了したら Enter を押してください..."
                read -r
            fi
        else
            warn "スキップしました（Homebrew のインストールに必要な場合があります）"
        fi
    fi

    echo ""
}

# ---------------------------------------------------------------------------
# Phase 3: Homebrew のインストール
# ---------------------------------------------------------------------------
phase_homebrew() {
    info "===== Phase 3: Homebrew のインストール ====="

    if command -v brew &>/dev/null; then
        success "Homebrew はインストール済みです: $(brew --version | head -1)"
    else
        if confirm "Homebrew をインストールしますか？"; then
            info "Homebrew をインストールしています..."
            run /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

            if ! "${DRY_RUN}"; then
                # Apple シリコンの場合、PATH に追加
                if [[ "$(uname -m)" == "arm64" ]]; then
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                    info "シェルプロファイルに Homebrew PATH を追加してください:"
                    echo '  echo '\''eval "$(/opt/homebrew/bin/brew shellenv)"'\'' >> ~/.zprofile'
                fi
            fi
        else
            error "Homebrew がないとパッケージのインストールができません"
            exit 1
        fi
    fi

    echo ""
}

# ---------------------------------------------------------------------------
# Phase 4: Brewfile からパッケージをインストール
# ---------------------------------------------------------------------------
phase_brew_bundle() {
    info "===== Phase 4: Brewfile からパッケージをインストール ====="

    # Brewfile の内容をプレビュー
    local tap_count formula_count cask_count mas_count
    tap_count=$(grep -c '^tap ' "${BREWFILE_PATH}" 2>/dev/null || echo 0)
    formula_count=$(grep -c '^brew ' "${BREWFILE_PATH}" 2>/dev/null || echo 0)
    cask_count=$(grep -c '^cask ' "${BREWFILE_PATH}" 2>/dev/null || echo 0)
    mas_count=$(grep -c '^mas ' "${BREWFILE_PATH}" 2>/dev/null || echo 0)

    info "インストール対象:"
    echo "  Tap:      ${tap_count}"
    echo "  Formula:  ${formula_count}"
    echo "  Cask:     ${cask_count}"
    echo "  MAS:      ${mas_count}"
    echo ""

    if confirm "Brewfile の内容をすべてインストールしますか？"; then
        info "brew bundle install を実行しています..."
        if "${DRY_RUN}"; then
            dry "brew bundle install --file=${BREWFILE_PATH} --verbose --no-lock"
            dry ""
            dry "インストール対象の詳細:"
            while IFS= read -r line; do
                # コメント行と空行をスキップ
                [[ "${line}" =~ ^#.*$ || -z "${line}" ]] && continue
                dry "  ${line}"
            done < "${BREWFILE_PATH}"
        else
            # brew bundle は個別パッケージの失敗でも続行する
            if brew bundle install --file="${BREWFILE_PATH}" --verbose --no-lock 2>&1 | tee -a "${LOG_FILE}"; then
                success "すべてのパッケージがインストールされました"
            else
                warn "一部のパッケージのインストールに失敗しました（ログを確認してください）"
            fi
        fi
    else
        warn "パッケージのインストールをスキップしました"
    fi

    echo ""
}

# ---------------------------------------------------------------------------
# Phase 5: インストール結果のサマリー
# ---------------------------------------------------------------------------
phase_summary() {
    echo ""
    echo "==========================================================================="
    echo "  セットアップ結果サマリー"
    echo "==========================================================================="

    if "${DRY_RUN}"; then
        dry "dry-run モードのため、実際のインストールは行われていません"
        echo ""
        echo "  実際にインストールするには:"
        echo "    ./setup.sh"
        echo ""
    else
        # インストール済みパッケージの確認
        local installed_formula installed_cask
        installed_formula=$(brew list --formula 2>/dev/null | wc -l | tr -d ' ')
        installed_cask=$(brew list --cask 2>/dev/null | wc -l | tr -d ' ')

        echo "  インストール済み Formula: ${installed_formula}"
        echo "  インストール済み Cask:    ${installed_cask}"
        echo ""

        # 失敗したパッケージがあるか確認
        if brew bundle check --file="${BREWFILE_PATH}" &>/dev/null; then
            success "Brewfile のすべてのパッケージがインストール済みです"
        else
            warn "未インストールのパッケージがあります:"
            brew bundle check --file="${BREWFILE_PATH}" 2>&1 | tee -a "${LOG_FILE}" || true
        fi

        echo ""
        echo "  ログファイル: ${LOG_FILE}"
    fi

    echo "==========================================================================="
    echo ""
}

# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------
main() {
    # ログファイルの初期化
    if ! "${DRY_RUN}"; then
        echo "=== Mac Setup Log - $(date) ===" > "${LOG_FILE}"
    fi

    echo ""
    echo "==========================================================================="
    if "${DRY_RUN}"; then
        echo "  Mac セットアップツール [DRY-RUN モード]"
    else
        echo "  Mac セットアップツール"
    fi
    echo "==========================================================================="
    echo ""

    phase_system_check
    phase_xcode_clt
    phase_homebrew
    phase_brew_bundle
    phase_summary

    if ! "${DRY_RUN}"; then
        success "セットアップが完了しました！"
    fi
}

main "$@"
