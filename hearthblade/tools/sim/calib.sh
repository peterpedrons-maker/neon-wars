bash /tmp/srv.sh
for cfg in "5 1 med" "10 2 med" "20 4 med" "30 6 good" "40 8 bis" "50 10 bis" "60 12 bis"; do set -- $cfg; L=$1; Z=$2; K=$3; echo -n "L=$L z=$Z $K "; timeout 220 node sim.js guerreiro 5 $L $Z $K | grep "\"min\":5" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d['mlv'],d['lossPerKill'],d['cycle'],d['deaths'])"; done
