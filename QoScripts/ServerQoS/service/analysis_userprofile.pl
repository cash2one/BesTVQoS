#!bin/perl

sub binary_search(\@\@$) {
	my ($ref_b, $ref_e, $value) = (@_);
	#print "$value\n";
  my $start = 0;
  my $end = $#$ref_b;
  
  #print "$end\n";
  
  my $mid = 0;
  while ($start <= $end) {
  	$mid = int($start + (($end - $start)/2));
  	if ($value >= $ref_b->[$mid] && $value <= $ref_e->[$mid]) {
  		last;
  	}
  	elsif($value > $ref_e->[$mid]) {
  		$start = $mid + 1;
  	}
  	else {
  		$end = $mid - 1;
  	}
  }
  
  return $mid;
}

sub netip2hostip {
	my ($netip) = @_;
	$ip_0 = int($netip/256/256/256);
	$ip_1 = (int($netip/256/256))%256;
	$ip_2 = int($netip/256)%256;
	$ip_3 = $netip%256;
	
	$ip_3*256*256*256 + $ip_2*256*256 + $ip_1*256 + $ip_0;
}

sub get_ip_int {
	my ($ip_str) = @_;
	@ip = split /\./, $ip_str;
	
	$ip[0]*256*256*256 + $ip[1]*256*256 + $ip[2]*256 + $ip[3];
}

$ipdataf = shift @ARGV;
print "$ipdataf\n";
open FILE, "<$ipdataf";
while (<FILE>) {
	chomp;
	
	@element = split / /;
	
	push @ip_begin, $element[0];
	push @ip_end, $element[1];
	push @province, $element[2];
	push @isp, $element[3];
}
close FILE;

foreach $filename (@ARGV) {
	$i++;
	print "$i $filename\n";
	
	open FILE, "<$filename";
	$save_filename = "$filename"."_isp";
	open OUT, ">$save_filename";
	while(<FILE>) {
		chomp;
		
		@element = split /\|/;
		
		#user ip isp
		$idx = binary_search @ip_begin, @ip_end, get_ip_int($element[0]);
		$record_isp = $isp[$idx];
		$record_province = $province[$idx];		
		
		print OUT ("$element[0]|$element[1]|$element[2]|$element[3]|$element[4]|$element[5]|$record_isp|$record_province|\n");

	}
	
	close OUT;
	close FILE;
}
