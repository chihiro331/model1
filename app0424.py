import streamlit as st
import pandas as pd
from mip import *
from datetime import datetime, timedelta
import plotly.express as px


# ------------------model1.py---------------------------------------------------------------------------------------


##時間経過後の時刻を返す関数
def add_minutes_to_datetime(minute_to_add):
    # 指定された日時をdatetimeオブジェクトに変換
    dt = datetime(2000, 1, 1, 8, 30)
    # 指定された分数を加算
    later = dt + timedelta(minutes = minute_to_add)
    # 結果を返す
    return later


##ガントチャートの描画関数
def draw_schedule(df):
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Orders", color="BeforeAfter", text="TaskID")
    fig.update_yaxes(autorange="reversed") #縦軸を降順に変更
    fig.update_traces(textposition='inside', insidetextanchor='middle') # px.timelineの引数textを置く位置を内側の中央に変更
    st.plotly_chart(fig, use_container_width=True)


##最適化
def schedule(df):

    #定数用のデータの作成
    Imax = 20
    I = [i+1 for i in range(Imax)]

    #仕事iの前段取に要する時間
    a = ['前段取（分）']
    a.extend(df['前段取（分）'])

    #仕事iの自動施工に要する時間
    b = ['自動加工（分）']
    b.extend(df['自動加工（分）'])

    # 仕事iの作成数量
    c = ['作成数量']
    c.extend(df['作成数量'])

    #空問題の作成
    model = Model('Schedule')

    #決定変数の作成
    x = {}
    v = {}
    y = {}
    w = {}
    z = {}
    for i in I:
        x[i] = model.add_var(f'x{i}', var_type='B')
        v[i] = model.add_var(f'v{i}', var_type='B')
        y[i] = model.add_var(f'y{i}', var_type='B')
        w[i] = model.add_var(f'w{i}', var_type='B')
        z[i] = model.add_var(f'w{i}', var_type='B')


    #制約条件の追加
    ##昼休み終了まで
    model += xsum(a[i] * x[i] + b[i] * v[i] for i in I) <= 210
    for i in I:
        model += v[i] <= x[i]

    ##午後休み終了まで
    model += xsum((a[i] + b[i]) * x[i] + a[i] * y[i] + b[i] * w[i] for i in I) <= 420
    model += xsum((a[i] + b[i]) * y[i] for i in I) <= 165
    for i in I:
        model += w[i] <= y[i]

    ##定時10分前終了まで
    model += xsum((a[i] + b[i]) * (x[i] + y[i] + z[i]) for i in I) <= 530
    model += xsum((a[i] + b[i]) * z[i] for i in I) <= 100

    ##その他
    for i in I:
        model += x[i] + y[i] + z[i] <= 1


    #目的関数の設定
    model.objective = maximize(xsum(x[i]+v[i]+y[i]+w[i]+z[i] for i in I))

    #最適化の実行
    status = model.optimize()

    #最適化の結果出力
    if status == OptimizationStatus.OPTIMAL:

        orders = 1

        time = 0
        for i in I:
            if(v[i].x > 0):
                result["仕事名"].append(f"Task{i}_Before")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+a[i])
                time += a[i]
                result["順番"].append(orders)
                result["前後"].append("Before")

                result["仕事名"].append(f"Task{i}_After")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+b[i])
                time += b[i]
                result["順番"].append(orders)
                orders += 1
                result["前後"].append("After")

        for i in I:
            if(x[i].x > v[i].x):
                result["仕事名"].append(f"Task{i}_Before")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+a[i])
                time += a[i]
                result["順番"].append(orders)
                result["前後"].append("Before")

                result["仕事名"].append(f"Task{i}_After")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+b[i])
                time += b[i]
                result["順番"].append(orders)
                orders += 1
                result["前後"].append("After")

        #昼休みまたがっていない場合
        if time < 265:
            time = 265

        for i in I:
            if(w[i].x > 0):
                result["仕事名"].append(f"Task{i}_Before")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+a[i])
                time += a[i]
                result["順番"].append(orders)
                result["前後"].append("Before")

                result["仕事名"].append(f"Task{i}_After")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+b[i])
                time += b[i]
                result["順番"].append(orders)
                orders += 1
                result["前後"].append("After")

        for i in I:
            if(y[i].x > w[i].x):
                result["仕事名"].append(f"Task{i}_Before")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+a[i])
                time += a[i]
                result["順番"].append(orders)
                result["前後"].append("Before")

                result["仕事名"].append(f"Task{i}_After")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+b[i])
                time += b[i]
                result["順番"].append(orders)
                orders += 1
                result["前後"].append("After")

        #午後休みまたがっていない場合
        if time < 430:
            time = 430

        for i in I:
            if(z[i].x > 0):
                result["仕事名"].append(f"Task{i}_Before")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+a[i])
                time += a[i]
                result["順番"].append(orders)
                result["前後"].append("Before")

                result["仕事名"].append(f"Task{i}_After")
                result["仕事ID"].append(i)
                result["開始時間"].append(time)
                result["完了時間"].append(time+b[i])
                time += b[i]
                result["順番"].append(orders)
                orders += 1
                result["前後"].append("After")

        #データフレームの作成
        data = []
        for i in range(len(result["仕事名"])):
          data.append(dict(
              Start       = add_minutes_to_datetime(result["開始時間"][i]),
              Finish      = add_minutes_to_datetime(result["完了時間"][i]),
              TaskName        = result["仕事名"][i],
              TaskID      = result["仕事ID"][i],
              Orders        = result["順番"][i],
              BeforeAfter = result["前後"][i])

          )
        DF = pd.DataFrame(data)
        draw_schedule(DF)


    else:
        print('最適解が求まりませんでした。')

#----------------df_editor---------------------------------------------------------------------

# def df_editor():
#     df_edit = pd.DataFrame(np.arange(60).reshape(20, 3), columns=("仕事ID", "前段取（分）", "自動加工（分）"))
#     df_edited = st.data_editor(df_edit)
#     if st.button("確定"):
#         return df_edited

#----------------main---------------------------------------------------------------------

def main():
    # 画面全体の設定
    st.set_page_config(
        page_title="スケジュール最適化アプリ",
        page_icon="😃",
        layout="centered",
        # initial_sidebar_state="collapsed",
    )

    # サイドバーの設定
    # タイトルを設定
    st.markdown(
        """
        # スケジュール最適化アプリ

        + ##### 作業データを読み込み、スケジュールの最適化を行うアプリです。
        + ##### 設定が完了したら、下の「最適化実行」ボタンを押してください。
        """
    )

    # インプットデータの設定
    st.sidebar.markdown(
        """
        ## インプットデータの設定
        """
    )

    # 従業員数を設定
    st.sidebar.markdown(
        """
        ### 1. 従業員数を設定
        """
    )
    num_employees = st.sidebar.number_input(
        "従業員", min_value=1, max_value=3, value=1
    )

    # 加工機台数を設定
    st.sidebar.markdown(
        """
        ### 2. 加工機台数を設定
        """
    )
    num_auto = st.sidebar.number_input("自動加工機", min_value=1, max_value=2, value=1)
    num_manu = st.sidebar.number_input("手動加工機", min_value=0, max_value=2, value=0)



    # ファイルアップローダーの準備
    uploaded_file = st.file_uploader("作業データCSVファイルのアップロード", type="csv")
    # uploadファイルが存在するときだけ、csvファイルの読み込みがされる。
    if uploaded_file is not None:
      # コメント行をスキップして読み込んでくれる
        dataframe = pd.read_csv(uploaded_file, comment="#")
        # 表として書き出される
        st.write(dataframe)

    # 作業データを手入力する場合
    # if st.button("作業データを手入力"):
    #     dataframe = df_editor()
        
    # 最適化実行
    if st.button("最適化実行"):
        with st.spinner("計算中"):
          schedule(dataframe)



if __name__ == "__main__":
    main()
