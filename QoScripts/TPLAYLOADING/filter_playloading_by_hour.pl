#! /usr/bin/env perl

use FileHandle;

# filter by ott, video type, loading type, output: loading...
$date = shift @ARGV;
$hour = shift @ARGV;
$srv_type = shift @ARGV;
$version_file = shift @ARGV;
$input = shift @ARGV;

my @version_type=();

open HVERSION, "<${version_file}";
while(<HVERSION>) {
	chomp;
	my @elements = split / /;
	push @version_type, $elements[2];
}
close HVERSION;

my @video_type=(1, 2, 3, 4);  # (1=>"vod", 2=>"huikan", 3=>"live", 4=>"liankan");
my @loading_type=(1, 2, 3);  # (1=>"fbuffer", 2=>"stuck", 3=>"dbuffer");

my %values_map;
foreach $version_item(@version_type){
	foreach $video_item(@video_type){
		foreach $loading_item(@loading_type){
			$id="${version_item}_${video_item}_${loading_item}_${date}";
			$values_map{$id}="";
		}
	}
}

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
		
	@loadings = split /;/, $elements[16];
	foreach $loading(@loadings){

		@subitems = split /,/, $loading;
		if(@subitems == 5){  #subitems[4] loading_type
			$version=$elements[6];
			$idx = rindex $elements[6], "_";
			$version2 = substr $elements[6], 0, $idx;
			$version2 = $version2."_All";
			
			$video=$elements[9];
			$load=$subitems[4];
			$id="${version}_${video}_${load}_${date}";
			$id2="${version2}_${video}_${load}_${date}";
			if(exists($values_map{${id}})){
				$temp="$subitems[1] $subitems[2] $subitems[3] $subitems[4]\n";
				$values_map{${id}}.=$temp;
				$values_map{${id2}}.=$temp;
				#print $values_map{${id}}
			}
		}
	}
}

# write to files
foreach $version_item(@version_type){
	foreach $video_item(@video_type){
		foreach $loading_item(@loading_type){
			$id="${version_item}_${video_item}_${loading_item}_${date}";
			if(exists($values_map{${id}}) && (length $values_map{${id}} > 0)){
				$filename="./temp/${srv_type}/${date}/${version_item}+${video_item}+${loading_item}+${date}${hour}.log";		
				#print "$filename\n";	
				unlink $filename if -e ${filename};
				open OUT, "> ${filename}";
				print OUT $values_map{${id}};
				close OUT
			}
		}
	}
}

print "filter dbuffer end...\n";
