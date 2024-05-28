import streamlit as st
import os
import pandas as pd
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.title("Monstermart Report February 2024")

categories = ['Profit','Product Loss','Top Sales & Restock']

tabs = st.tabs(categories)

with tabs[0]:
    st.header('Analisis Gross Profit Vending Machine Monstermart Periode Februari 2024')
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    profit_trend = pd.read_csv("Profit Trend Feb.csv")
    profit_by_product = pd.read_csv("Profit By Product Feb.csv")
    profit_by_machine = pd.read_csv("Revenue By Machine Feb.csv")
    
    total_sales_revenue = profit_by_product['Sales Revenue'].sum()
    total_gross_profit = profit_by_product['Gross Profit'].sum()
    gross_profit_percentage = (total_gross_profit / total_sales_revenue) * 100
    
    # Fungsi untuk mengonversi angka menjadi format rupiah
    def format_rupiah(angka):
        formatted_angka = "Rp{:,.0f}".format(angka)
        return formatted_angka
    
    # Fungsi untuk mengonversi angka menjadi persentase dengan 2 digit di belakang koma
    def format_percentage(angka):
        formatted_angka = "{:.2f}%".format(angka)
        return formatted_angka
    
    # Mengonversi nilai sales dan gross profit ke format rupiah
    formatted_total_sales_revenue = format_rupiah(total_sales_revenue)
    formatted_total_gross_profit = format_rupiah(total_gross_profit)
    
    # Mengonversi gross profit percentage ke format persentase dengan 2 digit di belakang koma
    formatted_gross_profit_percentage = format_percentage(gross_profit_percentage)
    
    # # Menghitung total kerugian
    
    # Menampilkan metric dengan nilai yang telah diformat
    
    sales_feb, loss_feb = st.columns(2)
    
    with sales_feb:
        st.metric("Total Sales", value=formatted_total_sales_revenue)
    
    with loss_feb:
        st.metric("Total Loss", value="Rp1,658,821")
    
    profit_feb, percentage_feb = st.columns(2)
    
    with profit_feb:
        st.metric("Total Gross Profit", value=formatted_total_gross_profit)
    
    with percentage_feb:
        st.metric("Gross Profit Percentage", value=formatted_gross_profit_percentage)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    #################################################################
    
    st.subheader("Daily Trend of General Gross Profit and Quantity Sold")
    
    def plot_trend(profit_trend):
        # Membuat plot untuk gross profit
        gross_profit_plot = alt.Chart(profit_trend).mark_bar(color='lightblue', opacity=0.7).encode(
            x='Day:T',
            y=alt.Y('Gross Profit:Q', title='Gross Profit (IDR)', axis=alt.Axis(grid=False)),  # Menghilangkan garis grid
            tooltip=['Day:T', 'Gross Profit:Q']
        )
        
        # Membuat plot untuk quantity sold
        qty_sold_plot = alt.Chart(profit_trend).mark_line(point=True, color='orange').encode(
            x='Day:T',
            y=alt.Y('Qty Sold:Q', title='Quantity Sold', axis=alt.Axis(grid=False)),  # Menghilangkan garis grid
            tooltip=['Day:T', 'Qty Sold:Q']
        )
    
        # Menggabungkan kedua plot
        combined_plot = alt.layer(
            gross_profit_plot,
            qty_sold_plot
        ).resolve_scale(
            y='independent'
        )
        
        # Menampilkan plot di Streamlit
        st.altair_chart(combined_plot, use_container_width=True)
    
    # Memanggil fungsi plot_trend dengan DataFrame profit_trend
    plot_trend(profit_trend)
    
    st.write(f'<div style="text-align: justify">Trend profit dan quantity produk terjual per harinya menunjukkan penjualan yang fluktuatif.</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    ##########################################################################
    
    # Memastikan kolom 'Day' adalah tipe datetime
    profit_trend['Day'] = pd.to_datetime(profit_trend['Day'])
    
    # Menambahkan kolom hari dalam minggu
    profit_trend['Day of Week'] = profit_trend['Day'].dt.dayofweek  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    
    # Menghitung selisih penjualan per hari
    profit_trend['Sales Revenue Diff'] = profit_trend['Sales Revenue'].diff()
    
    # Menghitung rata-rata selisih penjualan per hari dalam minggu
    avg_diff_by_day = profit_trend.groupby('Day of Week')['Sales Revenue Diff'].mean()
    
    # Set up the Streamlit app
    st.subheader("Average Daily Sales Difference (Monday-Sunday)")
    
    # Plotting the results
    fig, ax = plt.subplots(figsize=(10, 6))
    avg_diff_by_day.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title('Rata-Rata Selisih Penjualan Harian (Senin-Minggu)')
    ax.set_xlabel('Hari dalam Minggu')
    ax.set_ylabel('Rata-Rata Selisih Penjualan')
    ax.set_xticks(range(7))
    ax.set_xticklabels(['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'])
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.tick_params(axis='x', rotation=0)
    st.pyplot(fig)
    
    st.write(f'<div style="text-align: justify">Rata-rata selisih penjualan setiap harinya terlihat turun paling besar pada hari Minggu dan naik paling drastis di hari Senin. Penjualan vending machine di area perkantoran dan sekolah kemungkinan sepi karena hari libur dan mulai ramai kembali pada hari kerja.</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    ##########################################################################
    
    def create_bar_chart(data, x_field, y_field, color, title, total_value, width=600, height=400):
        data[f'Percentage'] = (data[x_field] / total_value) * 100
        bar_chart = alt.Chart(data).mark_bar(color=color).encode(
            y=alt.Y(f'{y_field}:N', title=title, sort=None),
            x=alt.X(f'{x_field}:Q', title=f'{x_field} (IDR)', axis=alt.Axis(format=',.0f')),
            tooltip=[f'{y_field}:N', f'{x_field}:Q', alt.Tooltip('Percentage:Q', format='.2f', title='Percentage')]
        ).properties(
            width=width,
            height=height
        ).configure_axis(
            labelFontSize=10,
            titleFontSize=12
        )
        return bar_chart
    
    st.subheader("Top 15 Machines By Sales February 2024")
    sorted_profit_by_machine = profit_by_machine.sort_values(by='Sales', ascending=False)
    top_15_machines = sorted_profit_by_machine.head(15)
    bar_chart_top = create_bar_chart(top_15_machines, 'Sales', 'Machines', 'skyblue', 'Machines', total_sales_revenue)
    st.altair_chart(bar_chart_top, use_container_width=True)
    st.write('<div style="text-align: justify">Kelima belas vending machine berikut merupakan vending machine dengan jumlah penjualan tertinggi dan merupakan penghasil profit terbanyak pada periode Februari 2024.</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.subheader("Bottom 15 Machines By Sales February 2024")
    bottom_15_machines = sorted_profit_by_machine.tail(15)
    bar_chart_bottom = create_bar_chart(bottom_15_machines, 'Sales', 'Machines', 'salmon', 'Machines', total_sales_revenue)
    st.altair_chart(bar_chart_bottom, use_container_width=True)
    st.write('<div style="text-align: justify">Kelima belas vending machine berikut adalah yang penjualannya terendah dalam waktu 1 bulan pada periode Februari 2024 dan memungkinkan menjadi penyebab kerugian, jika biaya operasional untuk vending machine pada daftar tersebut per bulannya lebih tinggi daripada penjualannya.</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.subheader("Top 10 Products by Gross Profit February 2024")
    sorted_df = profit_by_product.sort_values(by='Gross Profit', ascending=False)
    top_10_products = sorted_df.head(10)
    bar_chart_top_products = create_bar_chart(top_10_products, 'Gross Profit', 'Product', 'skyblue', 'Product', total_gross_profit)
    st.altair_chart(bar_chart_top_products, use_container_width=True)
    st.write('<div style="text-align: justify">Air mineral merk Le Minerale 600ML merupakan produk yang menyumbang gross profit terbesar pada periode Februari 2024.</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.subheader("Bottom 10 Products by Gross Profit February 2024")
    bottom_10_products = sorted_df.tail(10)
    bar_chart_bottom_products = create_bar_chart(bottom_10_products, 'Gross Profit', 'Product', 'salmon', 'Product', total_gross_profit)
    st.altair_chart(bar_chart_bottom_products, use_container_width=True)
    st.write('<div style="text-align: justify">Berdasarkan grafik tersebut, ditemukan bahwa beberapa produk hanya menghasilkan gross profit yang sangat sedikit dalam penjualan satu bulan. Bahkan, produk YOUVIT Multivitamin dijual lebih murah dari harga modal produk karena tidak laku di pasaran, sehingga terdapat kerugian sebesar dua ribu rupiah.</div>', unsafe_allow_html=True)

with tabs[1]:
    # Load datasets
    fl_data = pd.read_csv('fltanggalperfebsortedbytanggalawal.csv')
    qty_data = pd.read_csv('qtylostpertanggal.csv')
    lost_products_data = pd.read_csv('lostproductsqty.csv')
    fl_produk_data = pd.read_csv('flprodukperfebsortedbyangka.csv')
    fl_mesin_data = pd.read_csv('flmesinperfebsortedbyangka.csv')
    fl_tanggal_data = pd.read_csv('fltanggalperfebsortedbyangka.csv')
    
    # Preprocess financial loss dataset
    fl_data['Date'] = pd.to_datetime(fl_data['Date'])
    fl_data['Financial Loss'] = fl_data['Financial Loss'].str.replace(',', '').astype(float)
    
    # Calculate total financial loss
    total_financial_loss = fl_data['Financial Loss'].sum() + 2000
    
    # Display summary
    st.header('Financial Loss Data for February 2024')
    st.write(f'Total Financial Loss: Rp{total_financial_loss:,.2f}')
    st.write("Financial Loss Percentage: 1.6%")
    
    
    ## Plot Time Series for Financial Losses
    fig_fl = px.line(fl_data, x='Date', y='Financial Loss', title='Financial Losses')
    fig_fl.update_layout(plot_bgcolor='#ffffe0')  # Soft background color (krem)
    fig_fl.update_traces(line=dict(color='#00008b'))  # Soft line color (warna biru tua)
    st.plotly_chart(fig_fl, use_container_width=True)
    
    # Display Top 5 Lost Products table
    st.subheader('Top 5 Lost Products')
    top_5_lost_products = lost_products_data.head(5).reset_index(drop=True)
    top_5_lost_products.index += 1
    st.write(top_5_lost_products)
    
    # Display option for more details on Top 5 Lost Products table
    if st.button('Click here for more details', key='lost_products_detail'):
        lost_products_data.index += 1
        st.write(lost_products_data)
    
    # Display Top 5 Financial Losses table by Products
    st.subheader('Top 5 Financial Losses by Products')
    top_5_fl_produk = fl_produk_data.head(5).reset_index(drop=True)
    top_5_fl_produk.index += 1  # Start index from 1
    st.write(top_5_fl_produk)
    
    # Display option for more details on Top 5 Financial Losses table by Products
    if st.button('Click here for more details (by Products)', key='fl_produk_detail'):
        fl_produk_data.index +=1
        st.write(fl_produk_data)
    
    # Display Top 5 Financial Losses table by Machine
    st.subheader('Top 5 Financial Losses by Machine')
    top_5_fl_mesin = fl_mesin_data.head(5).reset_index(drop=True)
    top_5_fl_mesin.index += 1  # Start index from 1
    st.write(top_5_fl_mesin)
    
    # Display option for more details on Top 5 Financial Losses table by Machine
    if st.button('Click here for more details (by Machine)', key='fl_mesin_detail'):
        fl_mesin_data.index += 1
        st.write(fl_mesin_data)
    
    # Display Top 5 Financial Losses table by Date
    st.subheader('Top 5 Financial Losses by Date')
    top_5_fl_tanggal = fl_tanggal_data.head(5).reset_index(drop=True)
    top_5_fl_tanggal.index += 1  # Start index from 1
    st.write(top_5_fl_tanggal)
    
    # Display option for more details on Top 5 Financial Losses table by Date
    if st.button('Click here for more details (by Date)', key='fl_tanggal_detail'):
        fl_tanggal_data.index += 1
        st.write(fl_tanggal_data)

with tabs[2]:
    df1 = pd.read_csv('AKULAKU_FEB.csv')
    df2 = pd.read_csv('ALLSEDAYU_FEB.csv')
    df3 = pd.read_csv('ARGAPURA2_FEB.csv')
    df4 = pd.read_csv('ARWANACITRA_FEB.csv')
    df5 = pd.read_csv('ASURANSIJIWAALAMIN_FEB.csv')
    df6 = pd.read_csv('AXA4_FEB.csv')
    df7 = pd.read_csv('AXAKUNINGAN1_FEB.csv')
    df8 = pd.read_csv('AXAKUNINGAN2_FEB.csv')
    df9 = pd.read_csv('AXAKUNINGAN3_FEB.csv')
    df10 = pd.read_csv('BAKRIEANDBROTHERLT27_FEB.csv')
    df11 = pd.read_csv('BNIRAWAMANGUN_FEB.csv')
    df12 = pd.read_csv('CBCGALLERY_FEB.csv')
    df13 = pd.read_csv('CLUSTERATHALIA1_FEB.csv')
    df14 = pd.read_csv('CLUSTERATHALIA2_FEB.csv')
    df15 = pd.read_csv('CLUSTERBLUERIVER2_FEB.csv')
    df16 = pd.read_csv('CVJAYAABADI3_FEB.csv')
    df17 = pd.read_csv('DIGNITASACADEMY_FEB.csv')
    df18 = pd.read_csv('GRAHAELNUSA_FEB.csv')
    df19 = pd.read_csv('GRIYAPATRIAGUESTHOUSE_FEB.csv')
    df20 = pd.read_csv('HALIM_FEB.csv')
    df21 = pd.read_csv('HONDAMTHARYONO_FEB.csv')
    df22 = pd.read_csv('HOTEL101_FEB.csv')
    df23 = pd.read_csv('HOTELHERMITAGE_FEB.csv')
    df24 = pd.read_csv('HOTELHILTON_FEB.csv')
    df25 = pd.read_csv('HOTELKEMPINSKI1_FEB.csv')
    df26 = pd.read_csv('HOTELMERCURE_FEB.csv')
    df27 = pd.read_csv('HOTELPARKHYATT_FEB.csv')
    df28 = pd.read_csv('HOTELWYNDHAM_FEB.csv')
    df29 = pd.read_csv('INDOCEMENT_FEB.csv')
    df30 = pd.read_csv('INDOCEMENT2_FEB.csv')
    df31 = pd.read_csv('INDOCEMENT3_FEB.csv')
    df32 = pd.read_csv('INDOCEMENT4_FEB.csv')
    df33 = pd.read_csv('INDOCEMENT5_FEB.csv')
    df34 = pd.read_csv('INDOCEMENT6_FEB.csv')
    df35 = pd.read_csv('INDOCEMENT7_FEB.csv')
    df36 = pd.read_csv('INDOCEMENT8_FEB.csv')
    df37 = pd.read_csv('INDOCEMENT10_FEB.csv')
    df38 = pd.read_csv('JHLSOLITAIRE_FEB.csv')
    df39 = pd.read_csv('KENGSINGTONOFFICETOWER_FEB.csv')
    df40 = pd.read_csv('KLINIKLALITABEKASI_FEB.csv')
    df41 = pd.read_csv('LABSCHOOL1_FEB.csv')
    df42 = pd.read_csv('LABSCHOOL2_FEB.csv')
    df43 = pd.read_csv('LIONVILLAGE1_FEB.csv')
    df44 = pd.read_csv('LIONVILLAGE2_FEB.csv')
    df45 = pd.read_csv('LIPPOTOWERHOLLAND_FEB.csv')
    df46 = pd.read_csv('LIPPOTOWERHOLLAND2_FEB.csv')
    df47 = pd.read_csv('LIPPOTOWERHOLLAND3_FEB.csv')
    df48 = pd.read_csv('MANULIFE1_FEB.csv')
    df49 = pd.read_csv('MANULIFE2_FEB.csv')
    df50 = pd.read_csv('MASJIDALAZHARBEKASI1_FEB.csv')
    df51 = pd.read_csv('MASJIDATTAIBIN_FEB.csv')
    df52 = pd.read_csv('MENARATHAMRIN_FEB.csv')
    df53 = pd.read_csv('MONSTERMART_FEB.csv')
    df54 = pd.read_csv('NEOSOHO_FEB.csv')
    df55 = pd.read_csv('NINERESIDENCE_FEB.csv')
    df56 = pd.read_csv('PADINASOHO_FEB.csv')
    df57 = pd.read_csv('PTBAKER&HUGHES_FEB.csv')
    df58 = pd.read_csv('PTBASF_FEB.csv')
    df59 = pd.read_csv('PTCCIE(INDOCEMENT11)_FEB.csv')
    df60 = pd.read_csv('PTINDOCEMENT9(GEDUNGGMO)_FEB.csv')
    df61 = pd.read_csv('PTMATRARODAPIRANTI1_FEB.csv')
    df62 = pd.read_csv('PTMATRARODAPIRANTI2_FEB.csv')
    df63 = pd.read_csv('PTMATRARODAPIRANTI3_FEB.csv')
    df64 = pd.read_csv('PTSINERGI_FEB.csv')
    df65 = pd.read_csv('PTTIMERINDO_FEB.csv')
    df66 = pd.read_csv('PTTOACOATING1_FEB.csv')
    df67 = pd.read_csv('PULOMAS1_FEB.csv')
    df68 = pd.read_csv('PULOMAS2_FEB.csv')
    df69 = pd.read_csv('PULOMAS4_FEB.csv')
    df70 = pd.read_csv('REGALSTUDIO_FEB.csv')
    df71 = pd.read_csv('ROYALENFIELDANTASARI_FEB.csv')
    df72 = pd.read_csv('RSCM1_FEB.csv')
    df73 = pd.read_csv('RSCM2_FEB.csv')
    df74 = pd.read_csv('RSCM3_FEB.csv')
    df75 = pd.read_csv('RSCM4_FEB.csv')
    df76 = pd.read_csv('RSDINDA_FEB.csv')
    df77 = pd.read_csv('RSIAPRATIWI_FEB.csv')
    df78 = pd.read_csv('RSJAKARTA2_FEB.csv')
    df79 = pd.read_csv('RSJAKARTA3_FEB.csv')
    df80 = pd.read_csv('RSUIFARMASI_FEB.csv')
    df81 = pd.read_csv('RSUIIGD_FEB.csv')
    df82 = pd.read_csv('RSUILOBBY_FEB.csv')
    df83 = pd.read_csv('RSUILT5_FEB.csv')
    df84 = pd.read_csv('SEKOLAHALAZHARGRANDWISATABEKASI_FEB.csv')
    df85 = pd.read_csv('SAMSUNGKUNINGAN1_FEB.csv')
    df86 = pd.read_csv('SAMSUNGKUNINGAN2_FEB.csv')
    df87 = pd.read_csv('SEKOLAHBSP_FEB.csv')
    df88 = pd.read_csv('SENTRATIMUR1_FEB.csv')
    df89 = pd.read_csv('SENTRATIMUR2_FEB.csv')
    df90 = pd.read_csv('SEKOLAHFAJAR_FEB.csv')
    df91 = pd.read_csv('SMARTHAPPYKIDS_FEB.csv')
    df92 = pd.read_csv('SMKTELKOM_FEB.csv')
    df93 = pd.read_csv('STREGIST1_FEB.csv')
    df94 = pd.read_csv('STREGIST2_FEB.csv')
    df95 = pd.read_csv('UNIPREPBSD1_FEB.csv')
    df96 = pd.read_csv('UNIPREPBSD2_FEB.csv')
    df97 = pd.read_csv('UNIPREPKELAPAGADING_FEB.csv')
    df98 = pd.read_csv('UNIPREPPONDOKINDAH_FEB.csv')
    df99 = pd.read_csv('UNIVBAKRIE1_FEB.csv')
    df100 = pd.read_csv('UNIVBAKRIE2_FEB.csv')
    df101 = pd.read_csv('UNIVBAKRIE3_FEB.csv')
    df102 = pd.read_csv('UNIVERSALLUGAGE1_FEB.csv')
    df103 = pd.read_csv('UNIVERSALLUGAGE2_FEB.csv')
    df104 = pd.read_csv('UNIVERSITASPANCASILA_FEB.csv')
    data = pd.read_csv('dfcombined.csv')
    alldata = pd.read_csv('combined.csv')
    
    def main():
        st.header('Vending Machine Top Sales')
        options = {
            'ALL': 'combined.csv',
            'AKULAKU': 'AKULAKU_FEB.csv',
            'ALL SEDAYU': 'ALLSEDAYU_FEB.csv',
            'ARGAPURA2': 'ARGAPURA2_FEB.csv',
            'ARWANA CITRA': 'ARWANACITRA_FEB.csv',
            'ASURANSI JIWA AL AMIN': 'ASURANSIJIWAALAMIN_FEB.csv',
            'AXA 4': 'AXA4_FEB.csv',
            'AXA KUNINGAN1': 'AXAKUNINGAN1_FEB.csv',
            'AXA KUNINGAN2': 'AXAKUNINGAN2_FEB.csv',
            'AXA KUNINGAN3': 'AXAKUNINGAN3_FEB.csv',
            'BAKRIE AND BROTHER LT 27': 'BAKRIEANDBROTHERLT27_FEB.csv',
            'BNI RAWAMANGUN': 'BNIRAWAMANGUN_FEB.csv',
            'CBC GALLERY': 'CBCGALLERY_FEB.csv',
            'CLUSTER ATHALIA 1': 'CLUSTERATHALIA1_FEB.csv',
            'CLUSTER ATHALIA 2': 'CLUSTERATHALIA2_FEB.csv',
            'CLUSTER BLUE RIVER 2': 'CLUSTERBLUERIVER2_FEB.csv',
            'CV JAYA ABADI 3': 'CVJAYAABADI3_FEB.csv',
            'DIGNITAS ACADEMY': 'DIGNITASACADEMY_FEB.csv',
            'GRAHA ELNUSA': 'GRAHAELNUSA_FEB.csv',
            'GRIYA PATRIA GUEST HOUSE': 'GRIYAPATRIAGUESTHOUSE_FEB.csv',
            'HALIM': 'HALIM_FEB.csv',
            'HONDA MT HARYONO': 'HONDAMTHARYONO_FEB.csv',
            'HOTEL 101': 'HOTEL101_FEB.csv',
            'HOTEL HERMITAGE': 'HOTELHERMITAGE_FEB.csv',
            'HOTEL HILTON': 'HOTELHILTON_FEB.csv',
            'HOTEL KEMPINSKI 1': 'HOTELKEMPINSKI1_FEB.csv',
            'HOTEL MERCURE': 'HOTELMERCURE_FEB.csv',
            'HOTEL PARK HYATT': 'HOTELPARKHYATT_FEB.csv',
            'HOTEL WYNDHAM': 'HOTELWYNDHAM_FEB.csv',
            'INDOCEMENT': 'INDOCEMENT_FEB.csv',
            'INDOCEMENT 2': 'INDOCEMENT2_FEB.csv',
            'INDOCEMENT 3': 'INDOCEMENT3_FEB.csv',
            'INDOCEMENT 4': 'INDOCEMENT4_FEB.csv',
            'INDOCEMENT 5': 'INDOCEMENT5_FEB.csv',
            'INDOCEMENT 6': 'INDOCEMENT6_FEB.csv',
            'INDOCEMENT 7': 'INDOCEMENT7_FEB.csv',
            'INDOCEMENT 8': 'INDOCEMENT8_FEB.csv',
            'INDOCEMENT 10': 'INDOCEMENT10_FEB.csv',
            'JHL SOLITAIRE': 'JHLSOLITAIRE_FEB.csv',
            'KENGSINGTON OFFICE TOWER': 'KENGSINGTONOFFICETOWER_FEB.csv',
            'KLINIK LALITA BEKASI': 'KLINIKLALITABEKASI_FEB.csv',
            'LAB SCHOOL 1': 'LABSCHOOL1_FEB.csv',
            'LAB SCHOOL 2': 'LABSCHOOL2_FEB.csv',
            'LION VILLAGE 1': 'LIONVILLAGE1_FEB.csv',
            'LION VILLAGE 2': 'LIONVILLAGE2_FEB.csv',
            'LIPPO TOWER HOLLAND': 'LIPPOTOWERHOLLAND_FEB.csv',
            'LIPPO TOWER HOLLAND 2': 'LIPPOTOWERHOLLAND2_FEB.csv',
            'LIPPO TOWER HOLLAND 3': 'LIPPOTOWERHOLLAND3_FEB.csv',
            'MANULIFE 1': 'MANULIFE1_FEB.csv',
            'MANULIFE 2': 'MANULIFE2_FEB.csv',
            'MASJID AL AZHAR BEKASI': 'MASJIDALAZHARBEKASI1_FEB.csv',
            'MASJID AT TAIBIN': 'MASJIDATTAIBIN_FEB.csv',
            'MENARA THAMRIN': 'MENARATHAMRIN_FEB.csv',
            'MONSTERMART': 'MONSTERMART_FEB.csv',
            'NEOSOHO': 'NEOSOHO_FEB.csv',
            'NINE RESIDENCE': 'NINERESIDENCE_FEB.csv',
            'PADINA SOHO': 'PADINASOHO_FEB.csv',
            'PT BAKER & HUGHES': 'PTBAKER&HUGHES_FEB.csv',
            'PT BASF': 'PTBASF_FEB.csv',
            'PT CCIE (INDOCEMENT11)': 'PTCCIE(INDOCEMENT11)_FEB.csv',
            'PT MATRA RODA PIRANTI 1': 'PTMATRARODAPIRANTI1_FEB.csv',
            'PT MATRA RODA PIRANTI 2': 'PTMATRARODAPIRANTI2_FEB.csv',
            'PT MATRA RODA PIRANTI 3': 'PTMATRARODAPIRANTI3_FEB.csv',
            'PT SINERGI': 'PTSINERGI_FEB.csv',
            'PT TIMERINDO': 'PTTIMERINDO_FEB.csv',
            'PT TOA COATING 1': 'PTTOACOATING1_FEB.csv',
            'PULOMAS 1': 'PULOMAS1_FEB.csv',
            'PULOMAS 2': 'PULOMAS2_FEB.csv',
            'PULOMAS 4': 'PULOMAS4_FEB.csv',
            'REGAL STUDIO': 'REGALSTUDIO_FEB.csv',
            'ROYAL ENFIELD ANTASARI': 'ROYALENFIELDANTASARI_FEB.csv',
            'RSCM 1': 'RSCM1_FEB.csv',
            'RSCM 2': 'RSCM2_FEB.csv',
            'RSCM 3': 'RSCM3_FEB.csv',
            'RSCM 4': 'RSCM4_FEB.csv',
            'RSDINDA': 'RSDINDA_FEB.csv',
            'RSIAPRATIWI': 'RSIAPRATIWI_FEB.csv',
            'RS JAKARTA 2': 'RSJAKARTA2_FEB.csv',
            'RS JAKARTA 3': 'RSJAKARTA3_FEB.csv',
            'RS UI FARMASI': 'RSUIFARMASI_FEB.csv',
            'RS UI IGD': 'RSUIIGD_FEB.csv',
            'RS UI LOBBY': 'RSUILOBBY_FEB.csv',
            'RSUI LT 5': 'RSUILT5_FEB.csv',
            'SEKOLAH AL AZHAR GRAND WISATA BEKASI': 'SEKOLAHALAZHARGRANDWISATABEKASI_FEB.csv',
            'SAMSUNG KUNINGAN 1': 'SAMSUNGKUNINGAN1_FEB.csv',
            'SAMSUNG KUNINGAN 2': 'SAMSUNGKUNINGAN2_FEB.csv',
            'SEKOLAH BSP': 'SEKOLAHBSP_FEB.csv',
            'SEKOLAH FAJAR': 'SEKOLAHFAJAR_FEB.csv',
            'SENTRA TIMUR 1': 'SENTRATIMUR1_FEB.csv',
            'SENTRA TIMUR 2': 'SENTRATIMUR2_FEB.csv',
            'SMART HAPPY KIDS': 'SMARTHAPPYKIDS_FEB.csv',
            'SMK TELKOM': 'SMKTELKOM_FEB.csv',
            'ST REGIST 1': 'STREGIST1_FEB.csv',
            'ST REGIST 2': 'STREGIST2_FEB.csv',
            'UNIPREP BSD 1': 'UNIPREPBSD1_FEB.csv',
            'UNIPREP BSD 2': 'UNIPREPBSD2_FEB.csv',
            'UNIPREP KELAPA GADING': 'UNIPREPKELAPAGADING_FEB.csv',
            'UNIPREP PONDOK INDAH': 'UNIPREPPONDOKINDAH_FEB.csv',
            'UNIV BAKRIE 1': 'UNIVBAKRIE1_FEB.csv',
           'UNIV BAKRIE 2': 'UNIVBAKRIE2_FEB.csv',
            'UNIV BAKRIE 3': 'UNIVBAKRIE3_FEB.csv',
            'UNIVERSAL LUGAGE 1': 'UNIVERSALLUGAGE1_FEB.csv',
            'UNIVERSAL LUGAGE 2': 'UNIVERSALLUGAGE2_FEB.csv',
            'UNIVERSITAS PANCASILA': 'UNIVERSITASPANCASILA_FEB.csv'
        }
        st.subheader('Top 10 Quantities Sold')
        selected_option = st.selectbox('Select Vending Machine', list(options.keys()))
        months = {'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'}
        selected_month = st.selectbox('Select Month', months)
        year = {'2024'}
        selected_year = st.selectbox('Select Year', year)
    
        df = pd.read_csv(options[selected_option])
        df_sorted = df.sort_values(by="Qty Sold", ascending=False)
        top_10 = df_sorted.head(10)
        st.write(top_10)
    
        st.title('Product Sales Time Series')
    
    
        df_combined = pd.read_csv('dfcombined.csv')
        df_combined['Transaction'] = pd.to_datetime(df_combined['Transaction'])
    
        products = df_combined['Product'].unique()
        selected_products = st.multiselect('Select Products', products, default=products[0])
    
        if not selected_products:
            st.warning("Please select at least one product.")
        else:
            frequencies = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}
            selected_frequency = st.selectbox('Select Frequency', list(frequencies.keys()))
    
            fig, ax = plt.subplots(figsize=(10, 6))
            
        for product in selected_products:
            filtered_df = df_combined[df_combined['Product'] == product]
            resampled_df = filtered_df.set_index('Transaction').resample(frequencies[selected_frequency]).size()
            resampled_df.plot(ax=ax, marker='o', label=product)
            
            for idx, value in resampled_df.items():
                ax.annotate(f'{value}', xy=(idx, value), xytext=(0, 5), textcoords='offset points', ha='center', fontsize=8)
    
        plt.xlabel('Date')
        plt.ylabel('Number of Sales')
        plt.title(f'Product Sales Time Series ({selected_frequency})')
        plt.legend(title='Products')
        plt.grid(True)
        st.pyplot(fig)
    
        
        st.title ('Product That Needs To Be Restocked')
        stock_needed = pd.read_csv('stokneed.csv')
        machines = stock_needed['Machine'].unique()
        selected_machine = st.selectbox('Select a machine', machines)
        filtered_df = stock_needed[stock_needed['Machine'] == selected_machine]
        last_10 = filtered_df.nlargest(10, 'Qty Needed')
        st.subheader(f'Product with the least quantity on {selected_machine}')
        st.write(last_10)
    
    
    if __name__ == "__main__":
        main()

css = '''
<style>
   button[data-baseweb="tab"] {
   font-size: 18px;
   margin: 0;
   width: 100%;
   }
</style>
'''

st.markdown(css, unsafe_allow_html=True)
