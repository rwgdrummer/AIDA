echo '[mysqld]' > /etc/mysql/conf.d/mysql.cnf
echo 'sql-mode="STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION"' >> /etc/mysql/conf.d/mysql.cnf
