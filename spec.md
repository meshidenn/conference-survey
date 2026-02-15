# アプリ概要
学会でpublishされたpaperについて、概要とその年の傾向を簡単に把握するためのアプリです。

# やりたいこと
## メインのユースケース
1. ユーザはサーベイしたい学会を指定。
2. 指定された学会のaccepted papperのリストを作成
3. 各accepted paperのabstractから分類するためのタグを作成(別サーバーのlocal llmを使う)
3.1. タグを生成したら、階層化したり、似たようなタグをまとめたりする
4. 同じタグに属するpaperについて、そのタグ全体の要約を作成する
4.1. 階層化したら、下位のタグから要約を作成すること。
4.2. 上位のタグについては、各タグの要約をつかって要約を作成すること。
5. 同じタグに属するpaperについて、タグの要約と比較して、そのpaperは何が特徴的かのべること。
6. マインドマップで見やすくすること。

## 追加機能
1. タグについて、どれが何件だったかわかるページを用意すること。


# 将来構想。
1. 同じ学会が前年と比較してどう変化したかわかるようにしたい。
1.1. おそらく、タグについて整合性を取る必要がある。

2. 異なる学会で、似たような話題があるかしりたいo

3. まずはユーザが入力するが、将来的には、accepted paperが公開された時点で、自動でできるようになってほしい。


# 情報源
1. ACL系の学会(ACL, NAACL, EMNLP EACL): https://aclanthology.org/
2. COLM: https://openreview.net/group?id=colmweb.org/COLM
3. ICLR: https://iclr.cc/
3. ICML: https://icml.cc/
3. NeurIPS: https://neurips.cc/
3. AAAI: https://aaai.org/aaai-publications/aaai-conference-proceedings/
4. 画像処理系の学会(CVPR, ICCV, ECCV): https://openaccess.thecvf.com/menu
5. ACM系(KDD, SIGIR, CIKM): https://dl.acm.org/proceedings
