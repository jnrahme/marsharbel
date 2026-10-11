cd /home/sandbox/marsharbel/story-production/augustine
for k in $(seq 1 80); do python3 gen2.py >> /tmp/g3.log 2>&1; grep -q '^DONE' /tmp/g3.log && break; done
echo LOOPEND >> /tmp/g3.log
