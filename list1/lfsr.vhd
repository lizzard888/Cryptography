library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
library std;

entity lfsr is
    Generic( N : positive := 32 );
    Port ( clk : in  STD_LOGIC;
           ld  : in STD_LOGIC;
           data: in  STD_LOGIC_VECTOR(N-1 downto 0) := (OTHERS => '0');
           R   : out STD_LOGIC
			);
end lfsr;

ARCHITECTURE first OF lfsr IS
  signal q : STD_LOGIC_VECTOR(18 downto 0) := (OTHERS => '0');
BEGIN
  PROCESS(clk, ld, data)
  BEGIN
    if(ld = '1')
    then
      q <= data;
    elsif(clk'event and clk = '1')
    then
	    q(18 downto 1) <= q(17 downto 0);
	    q(0) <= not(q(18) XOR q(17) XOR q(16) XOR q(13));
    end if;
  END PROCESS;
  R <= q(18);
END first;

ARCHITECTURE second OF lfsr IS
  signal q : STD_LOGIC_VECTOR(21 downto 0) := (OTHERS => '0');
BEGIN
  PROCESS(clk, ld, data)
  BEGIN
    if(ld = '1')
    then
      q <= data;
    elsif(clk'event and clk = '1')
    then
	    q(21 downto 1) <= q(20 downto 0);
	    q(0) <= not(q(21) XOR q(20));
    end if;
  END PROCESS;
  R <= q(21);
END second;

ARCHITECTURE third OF lfsr IS
  signal q : STD_LOGIC_VECTOR(22 downto 0) := (OTHERS => '0');
BEGIN
  PROCESS(clk, ld, data)
  BEGIN
    if(ld = '1')
    then
      q <= data;
    elsif(clk'event and clk = '1')
    then
	    q(22 downto 1) <= q(21 downto 0);
	    q(0) <= not(q(22) XOR q(21) XOR q(20) XOR q(7));
    end if;
  END PROCESS;
  R <= q(22);
END third;
