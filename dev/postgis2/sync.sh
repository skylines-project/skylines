ssh skylines 'pg_dump -Fc -b -v skylines |bzip2' |bunzip2 |pg_restore -d skylines
