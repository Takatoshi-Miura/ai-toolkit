#!/usr/bin/env python3
"""
対話履歴可視化スクリプト

Gitコミット履歴から、ユーザーとClaudeの対話パターンを分析・可視化します。
"""

import subprocess
import re
from datetime import datetime
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
import numpy as np
import pandas as pd
from pathlib import Path

# 日本語フォント設定
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Noto Sans CJK JP']
rcParams['axes.unicode_minus'] = False

class InteractionHistoryVisualizer:
    """対話履歴を視覚化するクラス"""

    def __init__(self):
        self.commits = []
        self.load_git_history()

    def load_git_history(self):
        """Gitコミット履歴を読み込む"""
        try:
            result = subprocess.run(
                ['git', 'log', '--all', '--pretty=format:%ad|%s', '--date=short'],
                capture_output=True,
                text=True,
                check=True
            )

            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    date_str, message = line.split('|', 1)
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    self.commits.append({
                        'date': date,
                        'message': message
                    })
        except subprocess.CalledProcessError as e:
            print(f"Git履歴の取得に失敗しました: {e}")
            raise

    def extract_commit_type(self, message):
        """コミットメッセージからタイプを抽出"""
        match = re.match(r'\[(Add|Update|Fix|Remove)\]', message)
        if match:
            return match.group(1)
        return 'Other'

    def extract_keywords(self, message):
        """コミットメッセージからキーワードを抽出"""
        # タイプを除去
        message = re.sub(r'\[(Add|Update|Fix|Remove)\]\s*', '', message)

        # 主要なキーワード
        keywords = []
        keyword_patterns = {
            'コマンド': r'コマンド',
            'Skills': r'Skills|スキル',
            'プロンプト': r'プロンプト',
            'MCP': r'MCP',
            'レトロスペクティブ': r'レトロスペクティブ|振り返り',
            'テスト': r'テスト',
            'サブエージェント': r'サブエージェント|エージェント',
            'ニュース': r'ニュース',
            'レビュー': r'レビュー',
            'README': r'README|Readme',
            'Git': r'Git',
            'hook': r'hook',
        }

        for keyword, pattern in keyword_patterns.items():
            if re.search(pattern, message):
                keywords.append(keyword)

        return keywords

    def create_visualization(self, output_path):
        """視覚化を作成"""
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('Claude Code 対話履歴ダッシュボード',
                     fontsize=20, fontweight='bold', y=0.98)

        # グリッドレイアウト
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # 1. 時系列グラフ
        ax1 = fig.add_subplot(gs[0, :])
        self.plot_timeline(ax1)

        # 2. コミットタイプ円グラフ
        ax2 = fig.add_subplot(gs[1, 0])
        self.plot_commit_types(ax2)

        # 3. キーワード頻度
        ax3 = fig.add_subplot(gs[1, 1])
        self.plot_keywords(ax3)

        # 4. カレンダーヒートマップ
        ax4 = fig.add_subplot(gs[2, :])
        self.plot_calendar_heatmap(ax4)

        # 統計情報テキスト
        self.add_statistics(fig)

        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print(f"✓ 画像を生成しました: {output_path}")

    def plot_timeline(self, ax):
        """時系列グラフを描画"""
        dates = [c['date'] for c in self.commits]
        date_counts = Counter(dates)

        sorted_dates = sorted(date_counts.keys())
        counts = [date_counts[d] for d in sorted_dates]

        ax.plot(sorted_dates, counts, marker='o', linewidth=2,
               markersize=6, color='#2E86AB', label='コミット数')
        ax.fill_between(sorted_dates, counts, alpha=0.3, color='#2E86AB')

        ax.set_title('コミット活動の時系列推移', fontsize=14, fontweight='bold', pad=10)
        ax.set_xlabel('日付', fontsize=11)
        ax.set_ylabel('コミット数', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax.legend()

    def plot_commit_types(self, ax):
        """コミットタイプの円グラフを描画"""
        types = [self.extract_commit_type(c['message']) for c in self.commits]
        type_counts = Counter(types)

        colors = {
            'Add': '#06D6A0',
            'Update': '#118AB2',
            'Fix': '#EF476F',
            'Remove': '#FFD166',
            'Other': '#CCCCCC'
        }

        labels = list(type_counts.keys())
        sizes = list(type_counts.values())
        color_list = [colors.get(label, '#CCCCCC') for label in labels]

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=color_list,
                                           autopct='%1.1f%%', startangle=90,
                                           textprops={'fontsize': 10})

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('コミットタイプの分布', fontsize=14, fontweight='bold', pad=10)

    def plot_keywords(self, ax):
        """キーワード頻度のバーチャートを描画"""
        all_keywords = []
        for commit in self.commits:
            all_keywords.extend(self.extract_keywords(commit['message']))

        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(10)

        if top_keywords:
            keywords, counts = zip(*top_keywords)
            y_pos = np.arange(len(keywords))

            colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(keywords)))
            bars = ax.barh(y_pos, counts, color=colors)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(keywords, fontsize=10)
            ax.set_xlabel('出現回数', fontsize=11)
            ax.set_title('開発テーマ Top 10', fontsize=14, fontweight='bold', pad=10)
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3, axis='x', linestyle='--')

            # バーに数値を表示
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2,
                       f'{int(width)}',
                       ha='left', va='center', fontsize=9,
                       fontweight='bold', color='#333333')

    def plot_calendar_heatmap(self, ax):
        """カレンダーヒートマップを描画"""
        # 日付ごとのコミット数
        date_counts = Counter([c['date'].date() for c in self.commits])

        # 日付範囲を取得
        if not self.commits:
            return

        min_date = min(c['date'] for c in self.commits).date()
        max_date = max(c['date'] for c in self.commits).date()

        # 週ごとにデータを整理
        date_range = pd.date_range(min_date, max_date, freq='D')
        weeks = {}

        for date in date_range:
            week_num = date.isocalendar()[1]
            year = date.year
            weekday = date.weekday()
            key = f"{year}-W{week_num:02d}"

            if key not in weeks:
                weeks[key] = [0] * 7

            count = date_counts.get(date.date(), 0)
            weeks[key][weekday] = count

        # ヒートマップデータを作成
        week_labels = sorted(weeks.keys())
        heatmap_data = np.array([weeks[w] for w in week_labels]).T

        # プロット
        im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto',
                      interpolation='nearest')

        ax.set_yticks(np.arange(7))
        ax.set_yticklabels(['月', '火', '水', '木', '金', '土', '日'])
        ax.set_xticks(np.arange(len(week_labels)))
        ax.set_xticklabels(week_labels, rotation=45, ha='right', fontsize=8)
        ax.set_title('週間活動ヒートマップ', fontsize=14, fontweight='bold', pad=10)

        # カラーバー
        cbar = plt.colorbar(im, ax=ax, orientation='horizontal',
                           pad=0.05, aspect=30)
        cbar.set_label('コミット数', fontsize=10)

        # グリッド
        ax.set_xticks(np.arange(len(week_labels)) - 0.5, minor=True)
        ax.set_yticks(np.arange(7) - 0.5, minor=True)
        ax.grid(which='minor', color='white', linewidth=1.5)

    def add_statistics(self, fig):
        """統計情報を追加"""
        total_commits = len(self.commits)
        if not self.commits:
            return

        date_range = (max(c['date'] for c in self.commits) -
                     min(c['date'] for c in self.commits)).days + 1
        avg_commits_per_day = total_commits / date_range if date_range > 0 else 0

        types = [self.extract_commit_type(c['message']) for c in self.commits]
        type_counts = Counter(types)

        stats_text = f"""
        総コミット数: {total_commits}
        期間: {date_range}日間
        平均: {avg_commits_per_day:.2f}コミット/日

        Add: {type_counts.get('Add', 0)}  |  Update: {type_counts.get('Update', 0)}
        Fix: {type_counts.get('Fix', 0)}  |  Remove: {type_counts.get('Remove', 0)}
        """

        fig.text(0.02, 0.01, stats_text.strip(),
                fontsize=9, family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))


def main():
    """メイン処理"""
    print("=" * 60)
    print("Claude Code 対話履歴可視化")
    print("=" * 60)

    visualizer = InteractionHistoryVisualizer()

    if not visualizer.commits:
        print("✗ コミット履歴が見つかりませんでした")
        return

    print(f"✓ {len(visualizer.commits)}件のコミットを分析")

    output_path = Path('/home/user/ai-toolkit/interaction_history.png')
    visualizer.create_visualization(output_path)

    print(f"\n{'=' * 60}")
    print(f"完了！画像は以下のパスに保存されました：")
    print(f"{output_path}")
    print(f"{'=' * 60}\n")


if __name__ == '__main__':
    main()
