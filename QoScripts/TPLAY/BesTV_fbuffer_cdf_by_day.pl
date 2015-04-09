#! /usr/bin/env perl

$date = shift @ARGV;
$savedir = shift @ARGV;
$filename = shift @ARGV;

open FILE, "<$filename";
while(<FILE>) {
	chomp;
	@element = split /\|/;

	if($element[15]<0 || $element[15]>600) {
        next;
    }
	
	if ($element[31] == 1) {
        if ($element[15] <= 3) {
        	$suc += 1;
        }
	}
	
	$total += 1;
}
close FILE;

# for write results
$ratio = ($total == 0) ? 0 : $suc/$total;

open OUT, ">$savedir/BesTV_fbuffer_3s_ratio_data";
printf OUT ("|%s|%.2f|%d|%d|\n", $date, $ratio, $suc, $total);
close OUT;
