#! /usr/bin/env perl

use FileHandle;

$date = shift @ARGV;
$hour = shift @ARGV;
$input = shift @ARGV;
$out = shift @ARGV;

$b2c_type = "B2C";

my %fbuffer_map;
my %stuck_map;
my %stuck_dbuffer_map;
my %stucks_map;
my %stucks_dbuffers_map;

open FILE, "<${input}";
while(<FILE>) {
	chomp;
	@elements = split /\|/;
	if($elements[0] !~ /V1/){
		next;
	}
		
	# $16 loading
	# $9 video type
	# $6 version type
	
	$fbuffer=0;
	$stuck=0;
	$dbuffer=0;
	$fail=0;
	
	@loadings = split /;/, $elements[16];
	foreach $loading(@loadings){
		@subitems = split /,/, $loading;
		if(@subitems==5){  #subitems[4] loading_type
			if($subitems[4]==1){
				$fbuffer+=1;
			}elsif($subitems[4]==2){
				$stuck+=1;
			}elsif($subitems[4]==3){
				$dbuffer+=1;
			}elsif($subitems[4]==4){
				$fail+=1;
			}
		}
	}
	
	$version1 = $elements[6];
	$idx = rindex $elements[6], "_";
	$version2 = substr $elements[6], 0, $idx;
	$version2 = $version2."_All";
	
	$video=$elements[9];
	
	$id1="${version1} ${video}";
	$id2="${version2} ${video}";
	$fbuffer_map{$id1}+=1;
	$fbuffer_map{$id2}+=1;
	if($stuck>0){
		$stuck_map{$id1}+=1;
		$stuck_map{$id2}+=1;
	}
	
	if($stuck+$dbuffer>0){
		$stuck_dbuffer_map{$id1}+=1;
		$stuck_dbuffer_map{$id2}+=1;
	}
	
	$stucks_map{$id1}+=$stuck;
	$stucks_map{$id2}+=$stuck;
	$stucks_dbuffers_map{$id1}+=$stuck+$dbuffer;
	$stucks_dbuffers_map{$id2}+=$stuck+$dbuffer;
}
close FILE;

# write to files
foreach my $key( sort {$fbuffer_map{$b} <=> $fbuffer_map{$a}} keys %fbuffer_map){
	if(!exists($stuck_map{$key})){
		$stuck_map{$key}=0;
	}
	if(!exists($stuck_dbuffer_map{$key})){
		$stuck_dbuffer_map{$key}=0;
	}
	
	open OUT, ">> ${out}";
	printf OUT ("%s %d %s %s %d %d %d %d %d %.3f %.3f\n", ${date}, ${hour}, $b2c_type, $key, $fbuffer_map{$key}, $stuck_map{$key}, $stuck_dbuffer_map{$key}, 
		$stucks_map{$key}, $stucks_dbuffers_map{$key}, ($fbuffer_map{$key} - $stuck_map{$key})/$fbuffer_map{$key},
		($fbuffer_map{$key} - $stuck_dbuffer_map{$key})/$fbuffer_map{$key});
	close OUT;

	if($hour==24){
		@version_video = split / /, $key;
		open DIST, ">> ./out/total/playtm_of_$version_video[0]_$version_video[1]";
		printf DIST ("|%s|%s|%s|%d|%d|%d|%d|%d|%.3f|%.3f|\n", ${date}, $b2c_type, $key, $fbuffer_map{$key}, $stuck_map{$key}, $stuck_dbuffer_map{$key}, 
			$stucks_map{$key}, $stucks_dbuffers_map{$key}, , ($fbuffer_map{$key} - $stuck_map{$key})/$fbuffer_map{$key},
			($fbuffer_map{$key} - $stuck_dbuffer_map{$key})/$fbuffer_map{$key});
		close DIST;
	}
}

print "get playtm end...\n";
