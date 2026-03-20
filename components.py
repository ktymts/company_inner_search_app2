"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import streamlit as st
import utils
import constants as ct


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")


def display_select_mode():
    """
    回答モードのラジオボタンと利用説明をサイドバーに表示
    【問題3】対応: メインエリアからサイドバーへ移動（st.sidebar を使用）
    """
    with st.sidebar:
        # ==========================================
        # サイドバーの見出し
        # ==========================================
        st.markdown("利用目的")

        # 回答モードを選択するラジオボタンを表示
        # 「label_visibility="collapsed"」とすることで、ラジオボタンのラベルを非表示にする
        st.session_state.mode = st.radio(
            label="利用目的",
            options=[ct.ANSWER_MODE_1, ct.ANSWER_MODE_2],
            label_visibility="collapsed"
        )

        # ==========================================
        # 「社内文書検索」の機能説明
        # ==========================================
        st.markdown(f"**【「{ct.ANSWER_MODE_1}」を選択した場合】**")
        # 「st.info()」を使うと青枠で表示される
        st.info("入力内容と関連性が高い社内文書のありかを検索できます。")
        # 「st.code()」を使うとコードブロックの装飾で表示される
        # 「wrap_lines=True」で折り返し設定、「language=None」で非装飾とする
        st.code("【入力例】\n社員の育成方針に関するMTGの議事録", wrap_lines=True, language=None)

        # ==========================================
        # 「社内問い合わせ」の機能説明
        # ==========================================
        st.markdown(f"**【「{ct.ANSWER_MODE_2}」を選択した場合】**")
        st.info("質問・要望に対して、社内文書の情報をもとに回答を得られます。")
        st.code("【入力例】\n人事部に所属している従業員情報を一覧化して", wrap_lines=True, language=None)


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    【問題3】対応: モード説明はサイドバーに移動したため、メインエリアはシンプルな挨拶のみ表示
    """
    with st.chat_message("assistant"):
        # サイドバーで利用目的を選ぶよう案内する挨拶文
        st.markdown("こんにちは。私は社内文書の情報をもとに回答する生成AIチャットボットです。サイドバーで利用目的を選択し、画面下部のチャット欄からメッセージを送信してください。")

        # 「st.warning()」を使うと黄色枠で表示される
        st.warning("具体的に入力したほうが期待通りの回答を得やすいです。")


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    # 会話ログのループ処理
    for message in st.session_state.messages:
        # 「message」辞書の中の「role」キーには「user」か「assistant」が入っている
        with st.chat_message(message["role"]):

            # ユーザー入力値の場合、そのままテキストを表示するだけ
            if message["role"] == "user":
                st.markdown(message["content"])

            # LLMからの回答の場合
            else:
                # ==========================================
                # 「社内文書検索」の場合
                # ==========================================
                if message["content"]["mode"] == ct.ANSWER_MODE_1:

                    # ファイルのありかの情報が取得できた場合（通常時）の表示処理
                    if not "no_file_path_flg" in message["content"]:

                        # メインドキュメントの補足文を表示
                        st.markdown(message["content"]["main_message"])

                        # 参照元のありかに応じて、適したアイコンを取得
                        icon = utils.get_source_icon(message["content"]["main_file_path"])
                        # 【問題4】ページ番号が取得できた場合にのみ、ページ番号を表示
                        if "main_page_number" in message["content"]:
                            st.success(
                                f"{message['content']['main_file_path']}（ページNo.{message['content']['main_page_number']}）",
                                icon=icon
                            )
                        else:
                            st.success(f"{message['content']['main_file_path']}", icon=icon)

                        # サブドキュメントが存在する場合のみ表示
                        if "sub_message" in message["content"]:
                            # 補足メッセージの表示
                            st.markdown(message["content"]["sub_message"])

                            # サブドキュメントのありかを一覧表示
                            for sub_choice in message["content"]["sub_choices"]:
                                icon = utils.get_source_icon(sub_choice["source"])
                                # 【問題4】ページ番号が取得できた場合にのみ、ページ番号を表示
                                if "page_number" in sub_choice:
                                    st.info(
                                        f"{sub_choice['source']}（ページNo.{sub_choice['page_number']}）",
                                        icon=icon
                                    )
                                else:
                                    st.info(f"{sub_choice['source']}", icon=icon)

                    # ファイルのありかの情報が取得できなかった場合、LLMからの回答のみ表示
                    else:
                        st.markdown(message["content"]["answer"])

                # ==========================================
                # 「社内問い合わせ」の場合
                # ==========================================
                else:
                    # LLMからの回答を表示
                    st.markdown(message["content"]["answer"])

                    # 参照元のありかを一覧表示
                    if "file_info_list" in message["content"]:
                        # 区切り線の表示
                        st.divider()
                        # 「情報源」の文字を太字で表示
                        st.markdown(f"##### {message['content']['message']}")
                        # ドキュメントのありかを一覧表示
                        # 【問題4】file_info にはページ番号が含まれた文字列が格納済み
                        for file_info in message["content"]["file_info_list"]:
                            icon = utils.get_source_icon(file_info)
                            st.info(file_info, icon=icon)


def display_search_llm_response(llm_response):
    """
    「社内文書検索」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからのレスポンスに参照元情報が入っており、かつ「該当資料なし」でない場合
    if llm_response["context"] and llm_response["answer"] != ct.NO_DOC_MATCH_ANSWER:

        # ==========================================
        # メインドキュメントのありかを表示
        # ==========================================
        # context[0] が最も関連性の高いドキュメント
        main_file_path = llm_response["context"][0].metadata["source"]

        # 補足メッセージの表示
        main_message = "入力内容に関する情報は、以下のファイルに含まれている可能性があります。"
        st.markdown(main_message)

        # 参照元のありかに応じて、適したアイコンを取得
        icon = utils.get_source_icon(main_file_path)

        # 【問題4】ページ番号が取得できた場合のみページ番号を表示
        # ※LangChainのPDFローダーはページ番号を0始まりで格納するため、+1して表示する
        if "page" in llm_response["context"][0].metadata:
            main_page_number = llm_response["context"][0].metadata["page"] + 1
            st.success(f"{main_file_path}（ページNo.{main_page_number}）", icon=icon)
        else:
            st.success(f"{main_file_path}", icon=icon)

        # ==========================================
        # サブドキュメントのありかを表示
        # ==========================================
        sub_choices = []
        duplicate_check_list = []

        # context[1:]以降がサブドキュメント候補
        for document in llm_response["context"][1:]:
            sub_file_path = document.metadata["source"]

            # メインドキュメントと重複している場合はスキップ
            if sub_file_path == main_file_path:
                continue

            # 同ファイル内の別チャンクによる重複をスキップ
            if sub_file_path in duplicate_check_list:
                continue

            duplicate_check_list.append(sub_file_path)

            # 【問題4】ページ番号が取得できた場合のみ page_number を辞書に追加
            # ※+1して人間が読めるページ番号に変換
            if "page" in document.metadata:
                sub_page_number = document.metadata["page"] + 1
                sub_choice = {"source": sub_file_path, "page_number": sub_page_number}
            else:
                sub_choice = {"source": sub_file_path}

            sub_choices.append(sub_choice)

        # サブドキュメントが存在する場合のみ表示
        if sub_choices:
            sub_message = "その他、ファイルありかの候補を提示します。"
            st.markdown(sub_message)

            for sub_choice in sub_choices:
                icon = utils.get_source_icon(sub_choice["source"])
                # 【問題4】ページ番号が取得できた場合のみページ番号を表示
                if "page_number" in sub_choice:
                    st.info(
                        f"{sub_choice['source']}（ページNo.{sub_choice['page_number']}）",
                        icon=icon
                    )
                else:
                    st.info(f"{sub_choice['source']}", icon=icon)

        # 表示用の会話ログに格納するためのデータを用意
        content = {}
        content["mode"] = ct.ANSWER_MODE_1
        content["main_message"] = main_message
        content["main_file_path"] = main_file_path
        # ページ番号は取得できた場合のみ追加
        if "page" in llm_response["context"][0].metadata:
            content["main_page_number"] = main_page_number
        # サブドキュメントは存在する場合のみ追加
        if sub_choices:
            content["sub_message"] = sub_message
            content["sub_choices"] = sub_choices

    # 関連ドキュメントが見つからなかった場合
    else:
        st.markdown(ct.NO_DOC_MATCH_MESSAGE)

        content = {}
        content["mode"] = ct.ANSWER_MODE_1
        content["answer"] = ct.NO_DOC_MATCH_MESSAGE
        content["no_file_path_flg"] = True

    return content


def display_contact_llm_response(llm_response):
    """
    「社内問い合わせ」モードにおけるLLMレスポンスを表示

    Args:
        llm_response: LLMからの回答

    Returns:
        LLMからの回答を画面表示用に整形した辞書データ
    """
    # LLMからの回答を表示
    st.markdown(llm_response["answer"])

    # 回答に必要な情報が見つかった場合のみ情報源を表示
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        # 区切り線を表示
        st.divider()

        # 「情報源」の見出しを表示
        message = "情報源"
        st.markdown(f"##### {message}")

        file_path_list = []
        file_info_list = []

        for document in llm_response["context"]:
            file_path = document.metadata["source"]

            # ファイルパスの重複は除去
            if file_path in file_path_list:
                continue

            # 【問題4】ページ番号が取得できた場合のみページ番号を表示文字列に含める
            # ※LangChainのPDFローダーはページ番号を0始まりで格納するため、+1して表示する
            if "page" in document.metadata:
                page_number = document.metadata["page"] + 1
                file_info = f"{file_path}（ページNo.{page_number}）"
            else:
                file_info = f"{file_path}"

            # 参照元のありかに応じて、適したアイコンを取得
            icon = utils.get_source_icon(file_path)
            st.info(file_info, icon=icon)

            file_path_list.append(file_path)
            file_info_list.append(file_info)

    # 表示用の会話ログに格納するためのデータを用意
    content = {}
    content["mode"] = ct.ANSWER_MODE_2
    content["answer"] = llm_response["answer"]
    # 参照元ドキュメントが取得できた場合のみ追加
    if llm_response["answer"] != ct.INQUIRY_NO_MATCH_ANSWER:
        content["message"] = message
        content["file_info_list"] = file_info_list

    return content
