###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################
from cProfile import label

# 1. İş Problemi (Business Problem)
# 2. Veriyi Anlama (Data Understanding)
# 3. Veri Hazırlama (Data Preparation)
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
# 7. Tüm Sürecin Fonksiyonlaştırılması

###############################################################
# 1. İş Problemi (Business Problem)
###############################################################

# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
# pazarlama stratejileri belirlemek istiyor.

# Veri Seti Hikayesi
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.

# Değişkenler
#
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.


###############################################################
# 2. Veriyi Anlama (Data Understanding)
###############################################################

import pandas as pd
import datetime as dt
pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda x: "%3.f" % x)

df_ = pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2009-2010")
df = df_.copy()
df.head()
df.shape
df.isnull().values.any()
df.isnull().sum()

# Eşsiz ürün sayısı nedir
df["Description"].nunique()
df["Description"].value_counts()  #  Burda hangi üründen isminin kaç defa geçtiğini öğrendik
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
# Burda da hangi üründen kaçar tane satıldığına baktık ve bunları azalan şekilde sıraladık

df["Invoice"].nunique()

df["TotalPrice"] = df["Quantity"] * df["Price"]

df.groupby("Invoice").agg({"TotalPrice": ["sum", "mean"]}).head()





###############################################################
# 3. Veri Hazırlama (Data Preparation)
###############################################################
df.shape
df.isnull().sum()
df.dropna(inplace=True)  # Tüm eksik değerleri sildik
df.describe().T
# Şimdi bu veri setinde C ile başlayan yani iade olan ürünler mevcuttu bunlar da bize - değerler döndürüyor bunları
# veri setinden çıkarmamız lazım
df = df[~df["Invoice"].str.contains("C", na=False)]


###############################################################
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
###############################################################
df.head()
# Recency Frequency Monetary

df["InvoiceDate"].max()  # Son müşterinin geldiği tarih
# BUrda RFM metriklerinden Recency değerini bulmak için veri setinden Invoıce değerine sahip müşterinin en son geldiği
# tarihi bulacak ve  kve datetime fonksiyonu ile şimdiki tarihten çıkarmmazı lazım

today_day = dt.datetime(2010, 12, 11)
type(today_day)

# şimdi de bu değerleri tek tek hesaplayalim

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate: (today_day - InvoiceDate.max()).days,
                                    "Invoice": lambda Invoice: Invoice.nunique(),
                                     "TotalPrice": lambda TotalPrire: TotalPrire.sum()})

rfm.columns=["recency", "frequency", "monetary"]
rfm.head()

rfm.describe().T  # Burda hızlı bir betimlemesine bakarsak monetary min değeri 0 olan var ama bu işimizi görmüyor

rfm = rfm[rfm["monetary"] > 0]
rfm.describe().T  # Evet tekrardan baktıgımızda istemediğimiz değerleri sildik

rfm.shape  # Evet eldeki veri setini segmentlere ayırdık ve elimizdeki veri setini oldukça tekilleştirme işlemi yaptık
#  Burda RFM metriklerini tek tek hesapladık şimdi de bunları skorlara çevirmemiz gerekiyor




###############################################################
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
###############################################################

# şimdi burada skorlama işlemi yapacağız bunu da qcut metodu ile eldeki verileri tek tek parçalara ayırarak ve her bir
# parçaya birer label vererek onları daha okunabilir hale getireceğiz. Burda kaç parçaya ayırıp ayırmama sizin elinizde
# rfm skorlarını hesaplarken 1-5 aralığında hesaplamalar yapıldığı için ben 1-5 arası değer vercem

rfm["recency_scores"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
# Şimdi burda tam olarak ne yaptıgını açıklayalım örnek olarak yaş üzerinden gidelim. Mesela 1-100 arasına bakalım
# (1-100) 1-20, 20-40, 40-60, 60-80, 80-100----> bu şekilde gruplara ayırır ve verdiğimiz label sıralamasına göre
# eşleştirme yapar. Ancak dikkat edeceğimiz bir nokta Recency değeri ne kadar küçük olursa bizim için o kadar sıcak
# miştei demek oluyor o yüzden label verirken tersten vereceğiz yani küçük değere sahip olan müşteri label olarak
# yükseği alacak. Şimdi Frequency ve Monetary değerleri için de dilimleme işlemlri yapalım

rfm["frequency_scores"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
# Burda rank kullanma nedenimiz o kadar birbirini tekrar eden sayılar var ki bunu çeyreklemede zorlanıyor ve de hata
# alıyoruz. Bu durumu engelleme amacı ile ilk gördüğün değeri bir grup yap diyoruz

rfm["monetary_scores"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])
rfm.head()

# Şİmdi de bu değerleri iki boyuta getirip bir RFM skouru oluşturalım. Bizim için önemli olar Recency ve Monetary

rfm["RFM_Score"] = (rfm["recency_scores"].astype(str) + rfm["frequency_scores"].astype(str))
# Burda değerleri str yapma sebebimiz ıde int değerleri toplama olarak algılar ancak biz yan yana yazma istiyoruz
rfm.head()

# Şİmdi de elde ettiğimiz RFM_score den bazı değerleri alalım

rfm[rfm["RFM_Score"] =="55"]  # Bunlar bizim şammpiyon müşterilerimiz
rfm[rfm["RFM_Score"] =="11"]  # Bunlar da kaybedilmemsi gereken tehlikeli kaybedilecek müşteriler



###############################################################
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
###############################################################
# regex

# RFM isimlendirmesi. Elde edilen skorların neye karşılık geldiğini regex ile tanımlama işlemi yapıyoruz
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}


rfm["segment"] = rfm["RFM_Score"].replace(seg_map, regex=True)
rfm.head()
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])



# Şimdi mesela biz bunları kendi içinde de gruplandırdık regexlerini de verdik. Şirket bize dedi ki ben bunlardan mesela
# need_attention grubu ile özel olarak ilgilenmek istiyorum bana bunları at. şimdi de bunları csv fromatı ile aktaralım

rfm[rfm["segment"] == "champions"].head()
rfm[rfm["segment"] == "champions"].index  # bu o müşterilerin ID numaraları

new_df= pd.DataFrame()
new_df["new_customer_ID"] = rfm[rfm["segment"] == "new_customers"].index
# bu ıdlerde ondalıklı kısımları atalım

new_df["new_customer_ID"] = new_df["new_customer_ID"].astype(int)
# Evet yeni müşterilirimizin ID lerini alarak bunları bir dataframeye eldık ve bunları şimdi dışarı aktaralım
# Şimdi de bunu dışarı çıkarmak için csv formatına alalım

new_df.to_csv("new_customers.csv")

# yada tüm analizlerimizi dışarı aktaralım
rfm.to_csv("rfm.csv")




###############################################################
# 7. Tüm Sürecin Fonksiyonlaştırılması
###############################################################

def create_rfm(dataframe, csv=False):

    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df skorları kategorik değere dönüştürülüp df'e eklendi
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))


    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm


df = df_.copy()
create_rfm(df)