# HoYoLAB Cookie 取得ガイド

`/genshin status` コマンドのリアルタイム情報取得に必要なCookieの取得方法。

---

## 取得手順

1. ブラウザで [https://www.hoyolab.com/](https://www.hoyolab.com/) を開いてログイン

2. ブラウザの開発者ツールを開く
   - Chrome / Edge: `F12` または `Ctrl+Shift+I`
   - Firefox: `F12` または `Ctrl+Shift+I`
   - Safari: `Cmd+Option+I`

3. **Application** タブ（Chromeの場合）または **Storage** タブ（Firefoxの場合）を開く

4. 左サイドバーの **Cookies** → `https://www.hoyolab.com` を選択

5. 以下の2つの値をコピー：
   - `ltoken_v2`
   - `ltuid_v2`

---

## 使い方

```bash
python scripts/fetch.py status 861748604 \
  --ltoken <ltoken_v2の値> \
  --ltuid  <ltuid_v2の値>
```

---

## 注意事項

- **Cookieはセッション内でのみ使用し、ファイルに保存しない**
- Cookieには有効期限があり、定期的に再取得が必要
- 他人のCookieを使用しないこと
- これはmiHoYo非公式の方法であり、利用は自己責任

---

## ユーザーへの案内文（コピー用）

> リアルタイム情報（樹脂・派遣など）の取得にはHoYoLABのCookieが必要です。
>
> ① https://www.hoyolab.com をブラウザで開いてログイン
> ② 開発者ツール（F12）→ Application → Cookies → hoyolab.com
> ③ `ltoken_v2` と `ltuid_v2` の値をコピーして教えてください
>
> ⚠️ Cookieはこのセッション内でのみ使用します。
