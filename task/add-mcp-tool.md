# add-mcp-tool コマンド用タスク

## 概要
ユーザーの要件を聞き取り、Planサブエージェントで既存コードベースを調査・実装設計を立て、既存のMCPサーバーに新しいツールを追加します。

## 手順

### Phase 1: 要件ヒアリング

1. ユーザーに以下の質問をして情報を収集する

    ```
    既存のMCPサーバーに新しいツールを追加します。以下の情報を教えてください:

    【基本情報】
    - **MCPサーバーのディレクトリパス**: （絶対パス、例: ~/Documents/Git/MCP-GoogleDrive）
    - **ツール名**: （例: g_drive_merge_cell）
    - **ツールの説明**: （英語、例: Merge specified cell ranges in spreadsheets）

    【機能要件】
    - **対応ファイル種別**: （例: スプレッドシートのみ / ドキュメント / スライド / 複数対応）
    - **機能概要**: 何をするツールか（詳細に）
    - **引数の仕様**: どのようなパラメータを受け取るか
      - 引数名、型、必須/任意、説明
    - **実装場所**: どのサービスファイルに処理を追加するか
      - 例: sheets.service.ts / docs.service.ts / 新規ファイル

    【参考情報（オプション）】
    - **参考コード**: 似た機能を持つ既存ツール名
    - **API仕様**: 使用するGoogle API等のドキュメントURL
    ```

2. 収集した情報を整理して表形式でユーザーに確認する

    ```markdown
    ## 収集した要件

    ### 基本情報
    | 項目 | 内容 |
    |------|------|
    | MCPサーバーパス | {server_path} |
    | ツール名 | {tool_name} |
    | ツール説明 | {tool_description} |

    ### 機能要件
    | 項目 | 内容 |
    |------|------|
    | 対応ファイル種別 | {file_types} |
    | 機能概要 | {feature_summary} |
    | 実装場所 | {implementation_location} |

    ### 引数仕様
    | 引数名 | 型 | 必須/任意 | 説明 |
    |--------|-----|-----------|------|
    | {param1} | {type1} | {required1} | {desc1} |
    | {param2} | {type2} | {required2} | {desc2} |

    ### 参考情報
    - 参考ツール: {reference_tool}
    - API仕様: {api_doc_url}

    この内容で進めてよろしいですか？修正があればお知らせください。
    ```

3. 修正があれば再度確認し、承認を得る

### Phase 2: コードベース調査と実装設計

4. Taskツールを使用してPlanサブエージェントを起動し、既存コードベースの調査と実装設計を行う

    **プロンプト例:**
    ```
    以下の要件に基づいて、MCPツールの実装計画を立ててください。
    まず既存のコードベースを調査し、その後実装設計を提案してください。

    ## 収集した要件
    {collected_requirements}

    ## タスク
    ### Part 1: 既存コードベース調査
    以下を調査してください:
    1. MCPサーバーのディレクトリ構造
    2. 既存ツールの実装パターン
       - ツール定義ファイル（tools/*.tools.ts）
       - サービスロジック（services/*.service.ts）
       - 型定義（types/index.ts）
    3. 既存の類似ツールを参考実装として特定
    4. エラーハンドリングパターン
    5. README.md の構造（ツール一覧セクションの位置とフォーマット）

    ### Part 2: 実装設計
    調査結果を踏まえて、以下を提案してください:
    1. ツール定義の実装方針
       - zodスキーマ定義
       - パラメータバリデーション
       - エラーハンドリング
    2. サービスロジックの実装方針（必要な場合）
       - 処理フロー
       - Google API呼び出し方法
       - エラーハンドリング
    3. 必要な型定義の追加
    4. README更新箇所と内容
    5. 実装の優先順位とステップ

    既存の実装パターンを踏襲し、一貫性のある設計を提案してください。
    ```

5. Planサブエージェントから返された調査結果と実装計画をユーザーに提示する

    ```markdown
    ## コードベース調査結果と実装計画

    ### Part 1: 既存コードベース調査結果
    {codebase_analysis}

    ### Part 2: 実装計画
    {implementation_plan}

    この設計で進めてよろしいですか？修正があればお知らせください。
    ```

6. 修正があれば4-5を繰り返し、承認を得る

### Phase 3: ツール実装

7. サービスロジックの実装（必要な場合）
   - Readで既存のサービスファイルを読み込む
   - Editツールで新しいメソッドを追加
   - 実装計画で提案されたエラーハンドリングパターンを踏襲
   - 適切なコメントを追加（日本語可）

8. ツール定義の追加
   - Readでツール定義ファイル（tools/*.tools.ts）を読み込む
   - Editツールで新しいツールを追加
   - 実装計画で提案されたzodスキーマでパラメータを定義
   - 既存のツールと同じフォーマットに従う

    **実装例:**
    ```typescript
    server.tool(
      "{tool_name}",
      "{tool_description}",
      {
        fileId: z.string().describe("ID of the spreadsheet file"),
        fileType: z.enum(['sheets']).describe("File type: 'sheets' (spreadsheets only)"),
        range: z.string().describe("Cell range to merge (e.g., Sheet1!A1:B2)")
      },
      async ({ fileId, fileType, range }) => {
        try {
          const auth = await getAuthClient();
          const authError = checkAuthAndReturnError(auth);
          if (authError) return authError;

          // 実装内容

          return createSuccessResponse({
            status: "success",
            message: "処理が完了しました"
          });
        } catch (error: any) {
          return createErrorResponse("処理に失敗しました", error);
        }
      }
    );
    ```

9. 型定義の追加（必要な場合）
   - types/index.ts に新しい型を追加
   - Editツールを使用

10. 実装したコードを確認し、ユーザーに報告する

    ```markdown
    ## 実装完了

    ### 追加・変更したファイル
    - {file_path_1}: {description_1}
    - {file_path_2}: {description_2}

    ### 追加したツール
    - **ツール名**: `{tool_name}`
    - **説明**: {tool_description}
    - **パラメータ**:
      - {param1}: {desc1}
      - {param2}: {desc2}
    ```

### Phase 4: README更新

11. README.md のツール一覧セクションを更新する
    - Readで既存のREADME.md を読み込む
    - Editツールでツール一覧に新しいツールを追加
    - 実装計画で提案されたフォーマットに従う
    - 日本語で記載

    **追加例:**
    ```markdown
    ### {tool_name}

    {tool_description_ja}

    **パラメータ:**
    - `fileId` (string, 必須): スプレッドシートのファイルID
    - `range` (string, 必須): 結合するセル範囲（例: Sheet1!A1:B2）

    **使用例:**
    {usage_example}
    ```

12. その他のREADMEセクションも必要に応じて更新する
    - 機能一覧
    - 提供するツール数

### Phase 5: 動作確認の案内

13. ビルド・確認手順を案内する

    ```markdown
    ## 次のステップ

    ### ビルド
    ツールを追加したため、再ビルドが必要です:

    ```bash
    cd {server_path}
    npm run build
    ```

    ### Claude Desktop再起動
    ビルド後、Claude Desktopを再起動してください。

    ### 動作確認
    新しい会話で以下を確認してください:
    1. ツール `{tool_name}` が利用可能になっているか
    2. パラメータが正しく認識されるか
    3. 実際に実行してエラーが発生しないか

    ### テスト例
    ```
    （実際の使用例を提示）
    ```
    ```

14. トラブルシューティング情報を提供する

    ```markdown
    ## トラブルシューティング

    ### ビルドエラーが発生した場合
    - TypeScriptのコンパイルエラーがないか確認
    - 型定義が正しいか確認
    - 必要なimportが揃っているか確認

    ### ツールが認識されない場合
    - ビルドが成功しているか確認
    - Claude Desktopを完全に再起動したか確認
    - claude_desktop_config.json の設定が正しいか確認

    ### 実行時エラーが発生する場合
    - エラーメッセージを確認
    - 認証が正しく行われているか確認
    - パラメータの型が正しいか確認
    ```

15. 完了メッセージを表示

    ```markdown
    ## 完了

    MCPサーバー「{server_name}」に新しいツール「{tool_name}」を追加しました！

    ビルドして動作確認を行ってください。
    何か問題があればお知らせください。
    ```

## エラーハンドリング

| エラー状況 | 対処法 |
|-----------|--------|
| MCPサーバーパスが存在しない | パスの確認を依頼、エラーメッセージ表示 |
| ツール定義ファイルが見つからない | Grepで検索、ファイル構造の再確認 |
| 既存のツール名と重複 | 別名の提案、上書き確認 |
| ビルドエラー | コンパイルエラーの修正、依存関係の確認 |
| README更新失敗 | セクション構造の再確認、手動更新の案内 |

## 注意事項

- 既存のコードパターンを必ず踏襲する
- エラーハンドリングは既存のツールと同じ方法を使用する
- READMEは日本語で記載する
- ファイル編集前に既存の内容をバックアップとして確認する
- ツール名は既存のツールと重複しないようにする
- zodスキーマのdescribeは英語で記載する（MCP仕様に従う）
- コメントは日本語で記載してよい
- Planサブエージェントに既存コードベースの調査と実装設計を一括で任せる
