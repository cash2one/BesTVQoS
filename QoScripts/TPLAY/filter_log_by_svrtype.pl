#! /usr/bin/env perl

foreach $filename (@ARGV) {

	open FILE, "<$filename";
	print $filename."\n";

	while (<FILE>) {
		chomp;
		@element = split /\|/;
		
		#print $element[6]."\n";	
		
		if ($element[6] =~ /.*_A_.*/) {
			open SUBFILE1, ">>$filename\_B2C";
			print SUBFILE1 $_."\n";
			close SUBFILE1;
			
		} else {
			open SUBFILE2, ">>$filename\_B2B";
			print SUBFILE2 $_."\n";
			close SUBFILE2;
			
		}
	}

	close FILE;
}
