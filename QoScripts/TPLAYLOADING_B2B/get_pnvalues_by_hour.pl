#! /usr/bin/env perl

$date = shift @ARGV;
$hour = shift @ARGV;
$b2b_type = shift @ARGV;
$filename = shift @ARGV;
$out = shift @ARGV;

my %video_hash=(1=>"vod", 2=>"huikan", 3=>"live", 4=>"liankan");
my %load_hash=(1=>"fbuffer", 2=>"stuck", 3=>"dbuffer");

@file_id=split /[\/\+]/, $filename;

@ary=();

open FILE, "<$filename";
while(<FILE>) {
	chomp;
	@element = split / /;
	push @ary, $element[2];
}

@sorted_time = sort { $a <=> $b } @ary;
$suc_total = @sorted_time;
$idx_25 = $suc_total * 0.25;
$idx_50 = $suc_total * 0.50;
$idx_75 = $suc_total * 0.75;
$idx_90 = $suc_total * 0.90;
$idx_95 = $suc_total * 0.95;

$version=$file_id[4];
#print "version: $version\n";

if($suc_total>10){
	if(exists($video_hash{$file_id[5]}) && exists($load_hash{$file_id[6]})){
		open OUT, ">> ${out}";
		printf OUT ("%s %d %s %s %d %d %d %d %d %d %d %d\n", ${date}, ${hour}, ${b2b_type}, $version, $file_id[5], $file_id[6], $sorted_time[$idx_25], $sorted_time[$idx_50], $sorted_time[$idx_75], $sorted_time[$idx_90], $sorted_time[$idx_95], $suc_total);
		close OUT;
	}
}

