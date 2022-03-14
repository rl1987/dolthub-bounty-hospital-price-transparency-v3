# dolthub-bounty-hospital-price-transparency-v3

Code for Dolthub data bounty hospital-price-transparency-v3.

See: https://www.dolthub.com/repositories/dolthub/hospital-price-transparency-v3

To import scraped data into Dolt database, run:

```
$ for f in $(ls *.csv); do echo "$f"; dolt table import -u prices "$f"; done
$ cat hospitals.sql | dolt sql
```
