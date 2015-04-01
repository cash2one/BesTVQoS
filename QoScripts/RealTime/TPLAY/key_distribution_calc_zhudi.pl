#! /usr/bin/env perl

$svrtype = shift @ARGV;
$date = shift @ARGV;
$hour = shift @ARGV;
$key = shift @ARGV;
$written = shift @ARGV;

foreach $filename (@ARGV) {

	open FILE, "<$filename";
	print $filename."\n";

	while (<FILE>) {
		chomp;
		@element = split /\|/;

		@sub = split /_/, $element[6];
		pop @sub;
		$name = join("_", @sub);
		
		$count{$name}++;
			
		if ($written == 1) {
			open SUBFILE1, ">>tmp/${date}/$name\_hour";
			print SUBFILE1 $_."\n";
			close SUBFILE1;
		}
	}

	close FILE;
}

$outfilename = "$svrtype/$date/distribution_data_$key\_$hour";
open OUT, ">$outfilename";

foreach $key (sort {$count{$b}<=>$count{$a}} %count) {
	#print $key.",";
	if (defined($count{$key})) {
		#$total += $count{$key};
		print OUT "|$key|$count{$key}|\n";
	}
}

#print OUT "|total|$total|\n";

close OUT;
