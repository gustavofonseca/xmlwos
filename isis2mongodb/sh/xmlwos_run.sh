. xmlwos_config.sh

echo "Script running with CISIS version:"
$cisis_dir/mx what

colls=`ls -1 ../iso`
rm -f ../../databases/isis/artigo.*
rm -f ../../databases/isis/title.*
rm -f ../../databases/isis/bib4cit.*

for coll in $colls;
do
    echo "Creating now "$coll" master files"
    isos=`ls -1 ../iso/$coll/`
    for iso in $isos;
    do
        echo "Creating master files for "$iso
        dot_iso=`expr index "$iso" 1.`-1
        database_name=${iso:0:$dot_iso}
        $cisis_dir/mx iso=../iso/$coll/$iso append=../../databases/isis/$database_name -all now
    done
done

echo "Indexing databases according to FSTs"
$cisis_dir/mx ../../databases/isis/artigo  fst="@../fst/artigo.fst"  fullinv/ansi=../../databases/isis/artigo  tell=1000  -all now
$cisis_dir/mx ../../databases/isis/title   fst="@../fst/title.fst"   fullinv/ansi=../../databases/isis/title   tell=10    -all now
$cisis_dir/mx ../../databases/isis/bib4cit fst="@../fst/bib4cit.fst" fullinv/ansi=../../databases/isis/bib4cit tell=10000 -all now

echo "Creating articles processing list"
from=$1
count=$2
range=""

if [[ $from != "" ]]; then
    range="from="$from
fi

if [[ $count != "" ]]; then
    range=$range" count="$count
fi

articles_processing_list="aplf"$from"c"$count".txt"
$cisis_dir/mx ../../databases/isis/artigo "pft=if p(v880) then,v880,fi,/" $range -all now > ../tmp/$articles_processing_list

echo "Creating json files for each article"
mkdir -p ../output/isos/
total_pids=`wc -l ../tmp/$articles_processing_list`
from=1
for pid in `cat ../tmp/$articles_processing_list`;
do
    echo $from"/"$total_pids "-" $pid
    from=$(($from+1))

    loaded=`curl -s -X GET "http://"$scielo_data_url"/api/v1/is_loaded?code="$pid`
    if [[ $loaded == "False" ]]; then
        mkdir -p ../output/isos/$pid
        issn=${pid:1:9}
        len=${#pid}
        if [[ $len -eq 23 ]]; then
            $cisis_dir/mx ../../databases/isis/artigo  btell="0" pid=$pid   iso=../output/isos/$pid/$pid"_artigo.iso" -all now
            $cisis_dir/mx ../../databases/isis/title   btell="0" $issn      iso=../output/isos/$pid/$pid"_title.iso" -all now
            $cisis_dir/mx ../../databases/isis/bib4cit btell="0" $pid"$"    iso=../output/isos/$pid/$pid"_bib4cit.iso" -all now

            python isis2json.py ../output/isos/$pid/$pid"_artigo.iso" -c -p v -t 3 > ../output/isos/$pid/$pid"_artigo.json"
            python isis2json.py ../output/isos/$pid/$pid"_title.iso" -c -p v -t 3 > ../output/isos/$pid/$pid"_title.json"
            python isis2json.py ../output/isos/$pid/$pid"_bib4cit.iso" -c -p v -t 3 > ../output/isos/$pid/$pid"_bib4cit.json"
            curl -X POST "http://"$scielo_data_url"/api/v1/article?code="$pid
            rm -rf ../output/isos/$pid/*.iso
        fi
    else
        echo "article alread processed!!!"
    fi
done

deactivate
