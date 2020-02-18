# remove RDATE lines from the previous century (!) to reduce ics size
find . -type f -iname '*ics' -exec sed -i 'd/RDATE:19/' {} \+

# remove RDATE lines from last year to reduce ics size
find . -type f -iname '*ics' -exec sed -i 'd/RDATE:201/' {} \+
