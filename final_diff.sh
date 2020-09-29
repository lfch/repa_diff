#!/bin/bash 

diff_one()
{
	base=$1
	exp=$2
	result_file=$3

	cat $base | sort > $base.sorted
	cat $exp | sort > $exp.sorted

	res=`diff $base.sorted $exp.sorted`
	if [ -z "$res" ];
	then
	  echo "ok for $base" >> $result_file
	  echo "ok for $base"
	else
	  echo "not ok for $base" >> $result_file
	  echo "not ok for $base"
	fi
}

rm -f ./result/diff/*sorted*
rm -f ./result/diff_result

OLD_IFS="$IFS"
IFS=" "
names=`ls -l ./result/diff | awk '{print $9;}'`
names_string=`echo $names | awk -F " " '{printf("%s ", $0);}'`
array=($names_string)
for ((i=0;i<${#array[@]};i+=2))
do
	echo "$i ${array[i]}"
	echo "$((i+1)) ${array[$((i+1))]}"
	diff_one "./result/diff/${array[i]}" "./result/diff/${array[$((i+1))]}" "./result/diff_result"
done

IFS="$OLD_IFS"

rm -f ./result/diff/*sorted*
