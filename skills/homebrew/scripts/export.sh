#!/bin/bash
# =============================================================================
# export.sh - 現在のMac環境からBrewfileを生成するスクリプト
#
# 使い方: ./export.sh
# 旧Macで実行して、Homebrewパッケージ一覧をBrewfileとしてエクスポートする
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BREWFILE_PATH="${SCRIPT_DIR}/Brewfile"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------------------
# ユーティリティ関数
# ---------------------------------------------------------------------------
info()  { echo -e "\033[1;34m[INFO]\033[0m $*"; }
warn()  { echo -e "\033[1;33m[WARN]\033[0m $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*"; }
success() { echo -e "\033[1;32m[OK]\033[0m $*"; }

# ---------------------------------------------------------------------------
# 前提チェック
# ---------------------------------------------------------------------------
check_prerequisites() {
    info "前提条件を確認しています..."

    if ! command -v brew &>/dev/null; then
        error "Homebrew がインストールされていません"
        exit 1
    fi
    success "Homebrew が見つかりました: $(brew --version | head -1)"

    # mas (Mac App Store CLI) のチェック・インストール
    if ! command -v mas &>/dev/null; then
        warn "mas (Mac App Store CLI) がインストールされていません"
        read -rp "mas をインストールしますか？ (y/N): " answer
        if [[ "${answer}" =~ ^[Yy]$ ]]; then
            info "mas をインストールしています..."
            brew install mas
            success "mas をインストールしました"
        else
            warn "mas なしで続行します（Mac App Store アプリはエクスポートされません）"
        fi
    else
        success "mas が見つかりました: $(mas version)"
    fi
}

# ---------------------------------------------------------------------------
# Brewfile 生成
# ---------------------------------------------------------------------------
generate_brewfile() {
    info "Brewfile を生成しています..."

    # 既存ファイルのバックアップ
    if [[ -f "${BREWFILE_PATH}" ]]; then
        local backup="${BREWFILE_PATH}.bak.$(date +%Y%m%d%H%M%S)"
        cp "${BREWFILE_PATH}" "${backup}"
        warn "既存の Brewfile をバックアップしました: ${backup}"
    fi

    # brew bundle dump で Brewfile を生成
    local dump_opts=(--file="${BREWFILE_PATH}" --force --describe)

    # mas が利用可能なら Mac App Store アプリも含める
    if command -v mas &>/dev/null; then
        brew bundle dump "${dump_opts[@]}"
    else
        brew bundle dump "${dump_opts[@]}" --no-mas 2>/dev/null || brew bundle dump "${dump_opts[@]}"
    fi

    # ヘッダーコメントを追加
    local temp_file
    temp_file=$(mktemp)
    {
        echo "# ============================================================================="
        echo "# Brewfile - Mac 環境パッケージ定義"
        echo "# Generated: ${TIMESTAMP}"
        echo "# Host: $(hostname)"
        echo "# macOS: $(sw_vers -productVersion) ($(uname -m))"
        echo "# ============================================================================="
        echo ""
        cat "${BREWFILE_PATH}"
    } > "${temp_file}"
    mv "${temp_file}" "${BREWFILE_PATH}"

    success "Brewfile を生成しました: ${BREWFILE_PATH}"
}

# ---------------------------------------------------------------------------
# サマリー表示
# ---------------------------------------------------------------------------
show_summary() {
    echo ""
    echo "==========================================================================="
    echo "  エクスポート結果サマリー"
    echo "==========================================================================="

    local tap_count formula_count cask_count mas_count
    tap_count=$(grep -c '^tap ' "${BREWFILE_PATH}" 2>/dev/null || echo 0)
    formula_count=$(grep -c '^brew ' "${BREWFILE_PATH}" 2>/dev/null || echo 0)
    cask_count=$(grep -c '^cask ' "${BREWFILE_PATH}" 2>/dev/null || echo 0)
    mas_count=$(grep -c '^mas ' "${BREWFILE_PATH}" 2>/dev/null || echo 0)

    echo "  Tap:      ${tap_count}"
    echo "  Formula:  ${formula_count}"
    echo "  Cask:     ${cask_count}"
    echo "  MAS:      ${mas_count}"
    echo "  合計:     $(( tap_count + formula_count + cask_count + mas_count ))"
    echo ""
    echo "  出力先: ${BREWFILE_PATH}"
    echo "==========================================================================="
    echo ""
    info "次のステップ:"
    echo "  1. Brewfile の内容を確認し、不要なパッケージがあれば削除してください"
    echo "  2. このリポジトリをコミット・プッシュしてください"
    echo "  3. 新しい Mac で setup.sh を実行してください"
}

# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------
main() {
    echo ""
    echo "==========================================================================="
    echo "  Mac 環境エクスポートツール"
    echo "==========================================================================="
    echo ""

    check_prerequisites
    echo ""
    generate_brewfile
    show_summary
}

main "$@"
