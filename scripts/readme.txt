Using grabRatings.py:
    - Make sure that pysqlite2 is installed
    - Go to ROOT/databases
    - Create the DB file: ../scripts/grabRatings.py -f ../config/rate_my_professors.cfg -c -d rate_my_professors.db
    - Import into the database: ../scripts/grabRatings.py -f ../config/rate_my_professors.cfg -d rate_my_professors.db
    - The last command can be run in a cron job to pull latest ratings nightly/weekly

Creating statistics database:
    - Just run ROOT/scripts/createStatisticsDb.py
    - Ensure ROOT/databases and ROOT/databases/* are writable and readable by the web process
