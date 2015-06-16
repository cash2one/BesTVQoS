#! /usr/bin/env perl

$date = shift @ARGV;
$b2b_type = shift @ARGV;
$filename = shift @ARGV;
$output = shift @ARGV;

my %versions_dist;

open FILE, "<$filename";
while(<FILE>) {
	chomp;
	@elements = split /\|/;
	if($elements[0] !~ /V1/){
		next;
	}

	$version = $elements[6];
	$len = length $version;
	if($len<1){
		next;
	}

	$video=$elements[9];
	if($video !=1 && $video !=2 && $video !=3 && $video !=4){
		next;
	}

	$versions_dist{$elements[6]} += 1;
	$idx = rindex $elements[6], "_";
	$version2 = substr $elements[6], 0, $idx;
	$versions_dist{$version2."_All"} += 1;
}

$pout = $output;
open POUT, ">${pout}";

foreach my $key( sort {$versions_dist{$b} <=> $versions_dist{$a}} keys %versions_dist){
	printf POUT ("%s %s %s %d\n", $date, $b2b_type, $key, $versions_dist{$key});
}

close POUT;