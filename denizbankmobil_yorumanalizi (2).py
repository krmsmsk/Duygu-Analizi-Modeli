# -*- coding: utf-8 -*-
"""DenizBankMobil_YorumAnalizi.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1isBNf6mga9nHdG0eGrf3nzr2rR3LrnMR

**1. Android Marketten Yorumları Çekme**
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install google-play-scraper

## Burada doğru uygulamayı alabiliyor muyum diye kontrol ediyorum.

from google_play_scraper import app

# Uygulamanın uzantısı. Web adresinden aldım
app_package = 'com.denizbank.mobildeniz&gl=TR'

result = app(app_package)

# Başlıklar :
app_title = result['title']
developer = result['developer']
rating = result['score']
reviews = result['reviews']

# Yazdırıyorum :
print("Uygulama Adı:", app_title)
print("Geliştirici:", developer)
print("Derecelendirme:", rating)
print("Yorumlar:", reviews)

## Tüm yorumları yorumlar.txt adlı bir text dosyasına atıyorum.

from google_play_scraper import reviews_all

app_package = 'com.denizbank.mobildeniz'

# Uygulama yorumlarını çekmek için reviews_all()
result = reviews_all(
    app_package,
    lang='tr',  # Türkçe yorumları almak için 'tr'
)

# Elde edilen yorumları metin dosyasına yazdırma:
with open("yorumlar.txt", "w", encoding="utf-8") as file:
    for review in result:
        comment = review['content']
        file.write(comment + "\n")

"""**2. Veri Ön İşleme Adı**"""

from warnings import filterwarnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV, cross_validate
from sklearn.preprocessing import LabelEncoder
from textblob import Word, TextBlob
from wordcloud import WordCloud

filterwarnings('ignore') ## Bazı hataların önüne geçmek için, ignoreladım.
pd.set_option('display.max_columns', None) ## Tüm kolonları gösterdim.
pd.set_option('display.width', 200) ## Max genişliği 200 aldım. Rahat gözüksün diye.
pd.set_option('display.float_format', lambda x: '%.2f' % x) ## virgülden sonra 2 basamak göstermesi için.

AppFile = "/content/drive/MyDrive/DenizBank Mobil Yorumlar/yorumlar.txt"

# Metin dosyasını satır satır okuyarak verileri elde edin
with open(AppFile, "r", encoding="utf-8") as file:
    comments = [line.strip() for line in file]

# Verileri bir DataFrame'e dönüştürün
df = pd.DataFrame({"Yorumlar": comments})

print(df)

# Bütün yorumları küçük harf yapıyorum.
# İleride kullanacağım teknikler büyük küçük harf duyarlılığına sahip. Bu yüzden tüm kelimeleri küçük hafli yapıyorum.
df['Yorumlar'] = df['Yorumlar'].str.lower()

df['Yorumlar'] = df['Yorumlar'].str.replace('[^\w\s]', '') ## Noktalama işaretlerini boşluk ile değiştiriyorum.

## [^\w\s] bu ifade noktalama işaretlerini seçer.

df = df.drop(index=0) # Kısaltmalar kullanılan saçma bir yorum olduğu için kaldırdım.

df

## Duygu analiz sonuçlarımı kötü etkilediği için bu dört aşamayı yapmayacağım ama kodumda yer alacak. İleride kullanılması gerekilebilir.

# df['Yorumlar'] = df['Yorumlar'].str.replace('[\d]', '') ## [\d] metindeki sayıları seçer.

# sw = stopwords.words('turkish') ## Stopwordsleri sw değişkenine atadım. Nedir bu stopwordsler; "acaba, ama, birkaç, diye, eğer, gibi, hep, ki, kez" gibi kelimelerdir.
# df['Yorumlar'] = df['Yorumlar'].apply(lambda x: " ".join(x for x in str(x).split() if x not in sw))
## split() metodunun ön tanımlı dğeeri boşluktur. Bu yüzden ekstra bir şey yapmamıza gerek kalmadı.
## x for x in str(x) burada ise metni string olarak alıyorum.
## if x not in sw ile stopwords olanları eliyorum.
## lambda x: " ".join() ile de boşluklara göre birleştiriyorum. Kelimeler arasında boşluk bırakarak birleştirir.

# temp_df = pd.Series(' '.join(df['Yorumlar']).split()).value_counts()
## value_counts() ile kelimeleri saydırdım.
# drops = temp_df[temp_df <= 1] ## Burada metnin içinde bir ve ya daha az geçen kelimeleri yakalıyorum.
## Bu kelimeler ayırt edicilik için pek bir önem arz etmiyor.
# df['Yorumlar'] = df['Yorumlar'].apply(lambda x: " ".join(x for x in str(x).split() if x not in drops))
## 1 yada daha az geçen kelimeleri textten eledim.

# df['Yorumlar'] = df['Yorumlar'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
## Burada kelimeleri köklerine ayırıyorum.

"""**3. Sentiment Analysis**"""

!pip install transformers

## 13dk 56sn
import pandas as pd
from transformers import pipeline

sentiment_analysis_tr = pipeline("sentiment-analysis", model="savasy/bert-base-turkish-sentiment-cased")

data = df[:]

def analyze_sentiment(text):
  result = sentiment_analysis_tr(text)[0]
  label = result['label']
  return label


data['Duygu'] = data["Yorumlar"].apply(analyze_sentiment)

print(data)

data.to_csv("/content/drive/MyDrive/DenizBank Mobil Yorumlar/Yorumlar2.txt", sep='\t', index=False)

# DataFrame'deki "etiket" sütununu kullanarak pozitif ve negatif yorumları sayma
yorumlar = data['Yorumlar']
etiketler = data['Duygu']

# Pozitif yorumların sayısı
pozitif_yorumlar = yorumlar[etiketler == 'positive']
pozitif_yorum_sayisi = len(pozitif_yorumlar)

# Negatif yorumların sayısı
negatif_yorumlar = yorumlar[etiketler == 'negative']
negatif_yorum_sayisi = len(negatif_yorumlar)

# Sonuçları yazdırma
print("Pozitif yorum sayısı:", pozitif_yorum_sayisi)
print("Negatif yorum sayısı:", negatif_yorum_sayisi)

from collections import Counter

# Negatif yorumlardaki en çok tekrar eden satırı bulma
en_cok_tekrar_eden_satir_neg = Counter(negatif_yorumlar).most_common(1)
en_cok_tekrar_eden_satir_neg = en_cok_tekrar_eden_satir_neg[0][0]

# Pozitif yorumlardaki en çok tekrar eden satırı bulma
en_cok_tekrar_eden_satir_pos = Counter(pozitif_yorumlar).most_common(1)
en_cok_tekrar_eden_satir_pos = en_cok_tekrar_eden_satir_pos[0][0]

# Sonuçları yazdırma
print("Negatif yorumlardaki en çok tekrar eden satır:")
print(en_cok_tekrar_eden_satir_neg)
print("Pozitif yorumlardaki en çok tekrar eden satır:")
print(en_cok_tekrar_eden_satir_pos)

from collections import Counter

# Negatif yorumlardaki en çok tekrar eden satır ve frekansı
tekrar_sayilari_neg = Counter(negatif_yorumlar)
en_cok_gecen_10_satir_neg = tekrar_sayilari_neg.most_common(10)
neg_10 = pd.DataFrame(en_cok_gecen_10_satir_neg, columns = ['Yorum', 'Adet']) # İleride kullanmak için df 'e çevirdim.

# Pozitif yorumlardaki en çok tekrar eden satır ve frekansı
tekrar_sayilari_pos = Counter(pozitif_yorumlar)
en_cok_gecen_10_satir_pos = tekrar_sayilari_pos.most_common(10)
pos_10 = pd.DataFrame(en_cok_gecen_10_satir_pos, columns = ['Yorum', 'Adet'])

# Sonuçları yazdırma
print("Negatif yorumlardaki en çok geçen ilk 10 satır: ", en_cok_gecen_10_satir_neg)
print("Pozitif yorumlardaki en çok geçen ilk 10 satır: ", en_cok_gecen_10_satir_pos)

import nltk
nltk.download('stopwords') # Stopwords fonksiyonu için.
nltk.download('wordnet') # Lemmatize fonksiyonu için.

sw = stopwords.words('turkish') ## Stopwordsleri sw değişkenine atadım. Nedir bu stopwordsler; "acaba, ama, birkaç, diye, eğer, gibi, hep, ki, kez" gibi kelimelerdir.
negatif_yorumlar = negatif_yorumlar.apply(lambda x: " ".join(x for x in str(x).split() if x not in sw))
pozitif_yorumlar = pozitif_yorumlar.apply(lambda x: " ".join(x for x in str(x).split() if x not in sw))
## split() metodunun ön tanımlı dğeeri boşluktur. Bu yüzden ekstra bir şey yapmamıza gerek kalmadı.
## x for x in str(x) burada ise metni string olarak alıyorum.
## if x not in sw ile stopwords olanları eliyorum.
## lambda x: " ".join() ile de boşluklara göre birleştiriyorum. Kelimeler arasında boşluk bırakarak birleştirir.

negatif_yorumlar = negatif_yorumlar.apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
pozitif_yorumlar = pozitif_yorumlar.apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
## Burada kelimeleri köklerine ayırıyorum.

temp_df_neg = pd.Series(' '.join(negatif_yorumlar).split()).value_counts()
temp_df_pos = pd.Series(' '.join(pozitif_yorumlar).split()).value_counts()
## value_counts() ile kelimeleri saydırdım.

print(temp_df_neg)
print(temp_df_pos)

# En çok geçen ilk 10 kelimeyi yeni birer listeye atadım.
temp_df_neg_fnl = temp_df_neg[:10]
temp_df_pos_fnl = temp_df_pos[:10]

print(temp_df_neg_fnl)
print(temp_df_pos_fnl)

"""**4. Text Visualization**"""

## Datam toplamda 19.536 satırdan oluşuyor ve kelime bazlı saydırdığım için çok büyük bir data ortaya çıkıyor. Haliyle uygulama çöküyor. Bu yüzden aşağıda datadan bir örneklem alıp onu görselleştireceğim.

#pos_10 = en_cok_gecen_10_satir_pos
#neg_10 = en_cok_gecen_10_satir_neg

#tf = df2["Yorumlar"].apply(lambda x: pd.value_counts(x.split(" "))).sum(axis=0).reset_index()
## sum(axis=0) satır bazında ilgili kelimelerin frekanslarını toplamamızı sağlar.
## reset_index() okunabilir bir formata getirmek için indexlerini resetledim.

pos_10.plot.bar(x="Yorum", y="Adet") ## x ve y eksenlerini verdim.
plt.show()

neg_10.plot.bar(x="Yorum", y="Adet") ## x ve y eksenlerini verdim.
plt.show()

"""**5. Machine Learning Modeling**"""

data["Duygu"] = LabelEncoder().fit_transform(data["Duygu"])
## Kullanacak olduğum makine öğrenmesinin anlayacağı türden bir binary bağımlı değişkeni oluşturmuş oldum.

data

y = data["Duygu"] ## Bağımlı değişkenimiz.
X = data["Yorumlar"] ## Bağımsız değişkenimiz.

"""**5.1 Count Vector**




*   Elimizdeki texti (metni) öyle bir hale getirmeliyiz ki lineer cebir dünyasında işlenebilir bir hale gelsin.
Bunun için;
*   Count Vectors   : Frekans temsiller
*   TF-IDF Vectors  : Normalize edilmiş frekans temsiller


*   Word Embeddings (Word2Vec, Glove, BERT vs)

**5.2 TF_IDF**


*   CountVector 'ün ortaya çıkarabileceği bazı yanlılıkları gidermek adına; normalize edilmiş, standartlaştırılmış bir kelime vektörü oluşturma yöntemidir.
*   Kelimelerin dökümanlarda geçme frekansını ve kelimelerin tüm corpusta geçme frekansları odağında bir standartlaştırma işlemi yapılır.
"""

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
tf_idf_word_vectorizer = TfidfVectorizer()

X_tf_idf_word = tf_idf_word_vectorizer.fit_transform(X) ## Word model

tf_idf_ngram_vectorizer = TfidfVectorizer(ngram_range=(2,5))
X_tf_idf_ngram = tf_idf_ngram_vectorizer.fit_transform(X) ## ngram model

# ngram_range=(2,4) şu anlama gelmektedir:
# 2-gram'lar: "Bu ürün", "ürün gerçekten", "gerçekten çok", "çok kullanışlı", "kullanışlı ve", "ve kaliteli"
# 3-gram'lar: "Bu ürün gerçekten", "ürün gerçekten çok", "gerçekten çok kullanışlı", "çok kullanışlı ve", "kullanışlı ve kaliteli"
# 4-gram'lar: "Bu ürün gerçekten çok", "ürün gerçekten çok kullanışlı", "gerçekten çok kullanışlı ve", "çok kullanışlı ve kaliteli"
# yani 2li 3lü ve 4lü ngram modelleri oluşturur.

"""**5.3 Logistic Regression**"""

log_model = LogisticRegression().fit(X_tf_idf_word, y) ## Bağımsız değişken olarak son fit ettiğimiz word vektörümüzü verdim.

cross_val_score(log_model,
                X_tf_idf_ngram,
                y,
                scoring="accuracy",
                cv=10).mean() ## 10 katlı çapraz doğrulama yaparak modelin doğruluğunu (scoring="accuracy") test ettim.

## ngram model düşük başarı elde etti.

cross_val_score(log_model,
                X_tf_idf_word,
                y,
                scoring="accuracy",
                cv=10).mean() ## 10 katlı çapraz doğrulama yaparak modelin doğruluğunu (scoring="accuracy") test ettim.

while True:
  yorum = input("\n\nÇıkmak için 'çıkış' yazınız. \nYorumunuzu girin: ")
  if yorum == 'çıkış':
    break

  yeni_yorum = pd.Series([yorum])
  yeni_yorum = TfidfVectorizer().fit(X).transform(yeni_yorum)
  tahmin = log_model.predict(yeni_yorum)

  if tahmin == 0:
    tahmin_etiketi = "negatif"
  else:
    tahmin_etiketi = "pozitif"

  print("Yorum :", yorum, "-->Tahmin :", tahmin_etiketi)


print("Çıkış yapıldı.")

"""**5.4 Random Forest**"""

##count model
vectorizer = CountVectorizer()
X_count = vectorizer.fit_transform(X)
rf_model_1 = RandomForestClassifier().fit(X_count, y)
cross_val_score(rf_model_1, X_count, y, cv=10, n_jobs=-1).mean() ##n_jobs=-1 bütün işlemcileri kullan demektir.

##word model
rf_model_2 = RandomForestClassifier().fit(X_tf_idf_word, y)
cross_val_score(rf_model_2, X_count, y, cv=10, n_jobs=-1).mean()

## ngram model
rf_model = RandomForestClassifier().fit(X_tf_idf_ngram, y)
cross_val_score(rf_model, X_count, y, cv=10, n_jobs=-1).mean()

rf_model = RandomForestClassifier(random_state=17) ## random_state=17 ile her defasında aynı sonucu alırız.
## Sayıyı rastgele yazıyoruz.

rf_params = {"max_depth": [5, 8, None], ## max derinlik
             "max_features": [5, 7, "auto"], ## bölünmelerde göz önünde bulundurulacak özellik, değişken sayısı
             "min_samples_split": [2, 5, 8, 20], ## bölünmelerde bir yaprakta ne kadar örnek olması gerektiğinin parametresi
             "n_estimators": [100, 200, 500]} ## kaç tane ağaç fit edileceğini ifade eder

## Başarının değerlendirilmesi için; 1 saat 46dk 30sn
rf_best_grid = GridSearchCV(rf_model,
                            rf_params,
                            cv=10,
                            n_jobs=-1,
                            verbose=True).fit(X_count, y) ## verbose=True raporlama almamızı sağlar.

rf_best_grid.best_params_ ## Yukarıda en iyi sonuç veren parametreleri girdik.

rf_final = rf_model.set_params(**rf_best_grid.best_params_, random_state=17).fit(X_count, y)
## **rf_best_grid.best_params_ iki yıldız ile yazarsak, içindeki key ve valueları al demek olur.

# 3 satır yukarıdaki optimize işlemim çok uzun sürdüğü için onun sonuçlarını elle burada atıyorum:
rf_params = {"max_depth": None, ## max derinlik
             "max_features": 5, ## bölünmelerde göz önünde bulundurulacak özellik, değişken sayısı
             "min_samples_split": 2, ## bölünmelerde bir yaprakta ne kadar örnek olması gerektiğinin parametresi
             "n_estimators": 500}

rf_final = rf_model.set_params(**rf_params, random_state=17).fit(X_count, y)

## Son kez skorumuza bakalım.
cross_val_score(rf_final, X_count, y, cv=5, n_jobs=-1).mean()

while True:
  yorum = input("\n\nÇıkmak için 'çıkış' yazınız. \nYorumunuzu girin: ")
  if yorum == 'çıkış':
    break

  yeni_yorum = pd.Series([yorum])
  yeni_yorum = TfidfVectorizer().fit(X).transform(yeni_yorum)
  tahmin = rf_final.predict(yeni_yorum)

  if tahmin == 0:
    tahmin_etiketi = "negatif"
  else:
    tahmin_etiketi = "pozitif"

  print("Yorum :", yorum, "-->Tahmin :", tahmin_etiketi)


print("Çıkış yapıldı.")

## Yaptığım hatalı eklemeleri sildim.

import pandas as pd

data = pd.read_csv('/content/drive/MyDrive/DenizBank Mobil Yorumlar/Yorumlar2.txt', delimiter='\t')
data = data[:-1]

data

"""# **MODELİN TOPARLANMASI**
**FİNAL**

Bu aşamadan önce verileri çekip, ön işlemlerden geçirdim ki sağlık bir veri seti oluşsun. Tabi bunun için önce veri setini iyice anlamaya çalıştım. Ardından üzerinde bir çok denemeler yaparak işlenmeye en uygun hale getirdim. Burada bir sınıflandırma yaptığım için önce Logistic Regression sonra da Random Forest modellerini kurarak denedim. Başta elde ettiğim başarı oranı düşüktü bu yüzden geri gidip yaptığım bazı işlemleri iptal ettim, bazı yeni eklemeler yaptım. Ardından denediğimde Logistic Regression 'da %87, Random Forest 'ta %89 başarım elde ettim. Hiper parametre optimizasyonunu uyguladıktan sonra %90 'a çıkarabildim. Daha fazla başarım elde etmek için Hiper Parametre Optimizasyonuna biraz daha eğilinilebilinir fakat colab çok yavaş işlem yapıyor. Yaklaşık 2 saatte aldığım için sonuçları bu aşamada pek bir deneme yapamadım. Haliyle başarıyı arttırmak için artık veri setine yeni değişkenler eklemeli ve doğru sınıflandırma yapmalıyım diye düşünüyorum bu yüzden de modelimi programladım. Aşağı da detayları inceleyebilirsiniz.

Duygu sınıflandırmasını kullandığım kaynak : https://github.com/savasy/Turkish-Bert-NLP-Pipeline

Programı hızlı bir şekilde çalıştırabilmek için bilerek iki ayrı kod bloğuna böldüm. İlk kısım olan makine öğrenmesi kısmı 1 dk 10 sn civarında sonuçlanıyor.
İkinci kısım olan programlama kısmında çok fazla kez deneme yapmam gerektiği için her defasında modeli tekrar tekrar kurmasını beklemek istemedim.

Önemli Not : Programı çalıştırıp yeni yorumlar girerseniz, çıkış yazıp programı kapattığınızda yazdığınız tüm yeni yorumlar içeriye alınmaktadır. Bu şekilde sürekli büyüyen bir veri setini oluşturabildim. Bu kısım bence çok çok önemli.
Veri seti sürekli büyüdüğü için ilk blok olan modelleme kısmını her yeni yapılan kayıttan sonra tekrar çalıştırılmalıdır.
"""

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import re

data = pd.read_csv('/content/drive/MyDrive/DenizBank Mobil Yorumlar/Yorumlar2.txt', sep='\t').dropna()

data["Duygu"] = LabelEncoder().fit_transform(data["Duygu"])

y = data["Duygu"] ## Bağımlı değişkenimiz.
X = data["Yorumlar"] ## Bağımsız değişkenimiz.

vectorizer = CountVectorizer()
X_count = vectorizer.fit_transform(X)

tf_idf_word_vectorizer = TfidfVectorizer()
tf_idf_ngram_vectorizer = TfidfVectorizer(ngram_range=(2,5))
X_tf_idf_ngram = tf_idf_ngram_vectorizer.fit_transform(X)

rf_model = RandomForestClassifier().fit(X_tf_idf_ngram, y)
rf_params = {"max_depth": None,
             "max_features": 5,
             "min_samples_split": 2,
             "n_estimators": 500}

rf_final = rf_model.set_params(**rf_params).fit(X_count, y)

print("\nÇıkmak için 'çıkış' yazınız.")
print("\nEğer tahmin yanlışsa '0' yazın. \nDoğruysa '1' yazın: \n")

yeni_veriler = []

while True:
  print("------------------------")
  print("Yorumunuzu girin : ")
  yorum = input()
  if yorum == 'çıkış':
    break

  yorum = yorum.lower()
  yorum = re.sub(r'[^\w\s]', '', yorum)

  yeni_yorum = pd.Series([yorum])
  yeni_yorum_count = vectorizer.transform(yeni_yorum)
  tahmin = rf_final.predict(X_count[-1, :])

  if tahmin == 0:
    tahmin_etiketi = "negatif"
  else:
    tahmin_etiketi = "pozitif"

  print("-->Tahmin :", tahmin_etiketi)
  # Tahmin yanlışsa düzeltme yapılacak.
  print("Tahmin Doğru mu? (1/0)")
  duzeltme = 1
  duzeltme = int(input())
  if duzeltme == 0:
      tahmin = 1 - tahmin ## tahminin tersini alarak düzeltmiş olucaz.
      print("\nDüzeltme yapıldı.\n")
      if tahmin == 0:
          tahmin_etiketi = "negatif"
      else:
          tahmin_etiketi = "pozitif"
      print("Yorum: ", yorum, "--> Tahmin: ", tahmin_etiketi)


  yeni_veri = {"Yorumlar": yorum, "Duygu": tahmin}
  yeni_veriler.append(yeni_veri)

  # Yeni yorumu veri setine yükleme;
  #yeni_veri = pd.DataFrame.from_dict({"Yorumlar": [yorum], "Duygu": tahmin})
  #data = pd.concat([data, yeni_veri], ignore_index=True)


  # Veri kümesinin de güncellenmesi gerek;
  y = data["Duygu"] ## Bağımlı değişkenimiz.
  X = data["Yorumlar"] ## Bağımsız değişkenimiz.
  X_count = vectorizer.fit_transform(X)



  print("------------------------")


print("Çıkış yapıldı.")

yeni_veriler_df = pd.DataFrame(yeni_veriler)
yeni_veriler_df["Duygu"] = yeni_veriler_df["Duygu"].astype(int)  # Duygu sütununu integer tipine dönüştürme
data = pd.concat([data, yeni_veriler_df], ignore_index=True)

# Güncellenmiş veri kümesini dosyamıza yazdırıyoruz ki datalarımız büyüsün, modelimiz doğru tahminlerle gelişsin.
data.to_csv('/content/drive/MyDrive/DenizBank Mobil Yorumlar/Yorumlar2.txt', index=False, sep='\t')

print("Veri kümesi güncellendi.")

data

## Burada yaptığım hatalı eklemeleri siliyordum ki veri setini bozmadan tekrar tekrar deneyebileyim.

data = pd.read_csv('/content/drive/MyDrive/DenizBank Mobil Yorumlar/Yorumlar2.txt', delimiter='\t')
data = data[:-4]

data