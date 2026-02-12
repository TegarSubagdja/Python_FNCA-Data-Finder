import locale

locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

gaji = 3596000
totalgaji = gaji
totalaset = gaji
for i in range(5):
    count = 0.5 * totalaset
    totalgaji += gaji +(gaji*12)
    totalaset += totalgaji + count

print(f"Gaji yang ditabung adalah gaji {locale.currency(gaji, grouping=True)}")
print(f"Total yang didapatkan {locale.currency(totalaset, grouping=True)}")