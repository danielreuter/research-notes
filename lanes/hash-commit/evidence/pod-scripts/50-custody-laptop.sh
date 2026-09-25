ids=($(grep -o 'art:[0-9a-f]*' ~/.research/notes/lanes/hash-commit/evidence/registered-4090.txt))
done5="art:71a37756 art:4be5c412 art:381bcee8 art:9fdb64e0 art:abb219fa"
todo=(); for a in "${ids[@]}"; do case " $done5 " in *" ${a:0:12} "*) ;; *) todo+=($a);; esac; done
echo "todo ${#todo[@]}" > /Users/danielreuter/.research/notes/lanes/hash-commit/evidence/custody-4090.txt
for ((i=0; i<${#todo[@]}; i+=5)); do research data preserved --mode head "${todo[@]:$i:5}" >> /Users/danielreuter/.research/notes/lanes/hash-commit/evidence/custody-4090.txt 2>&1; echo "batch $i rc=$?" >> /Users/danielreuter/.research/notes/lanes/hash-commit/evidence/custody-4090.txt; done
echo DONE >> /Users/danielreuter/.research/notes/lanes/hash-commit/evidence/custody-4090.txt
