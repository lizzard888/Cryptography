library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
library std;

-- this is a testbench, but can be any other entity
entity lfsr_tb is
  end lfsr_tb;

architecture complex of lfsr_tb is
  -- this clock runs at HOW MANY MHz?
  constant clock_period : time := 10 ns;
  -- lfsr width
  constant first_width : positive := 19;
  constant second_width : positive := 22;
  constant third_width : positive := 23;
  -- clock signal
  signal clock : std_logic :=  '0';
  -- lines for loading-up LFSRs
  signal q1 : std_logic_vector(18 downto 0) := (others => '0');
  signal q2 : std_logic_vector(21 downto 0) := (others => '0');
  signal q3 : std_logic_vector(22 downto 0) := (others => '0');
  -- signal to start loading LFSRs
  signal load  : std_logic := '0';
  -- outputs from LFSRs
  signal LFSR1,LFSR2,LFSR3 : std_logic;
  signal RND : std_logic :=  '0';

  -- just a reminder what will be tested
  component lfsr
    Generic (N : positive);
    port(
          clk  : in STD_LOGIC;
          ld   : in STD_LOGIC;
          data : in STD_LOGIC_VECTOR(N-1 downto 0);
          R    : out STD_LOGIC );
  end component;

  -- remember? we defined two architectures for 'lfsr'
  for UUT1 : lfsr use entity work.lfsr(first);
  for UUT2 : lfsr use entity work.lfsr(second);
  for UUT3 : lfsr use entity work.lfsr(third);

begin
  -- let's create instances of our LFSRs
  UUT1 : lfsr
  GENERIC MAP ( N => first_width )
  port map ( clk => clock, ld => load, data => q1, R => LFSR1 );
  UUT2 : lfsr
  GENERIC MAP ( N => second_width )
  port map ( clk => clock, ld => load, data => q2, R => LFSR2 );
  UUT3 : lfsr
  GENERIC MAP ( N => third_width )
  port map ( clk => clock, ld => load, data => q3, R => LFSR3 );

  -- this will run infinitely, stopping every few ns
  clocker : process
  begin
    clock <= not clock;
    wait for clock_period/2;
    RND <= LFSR1 xor LFSR2;
    if(LFSR3 = '1')
    then
      write(output, " " & std_logic'image(RND)(2));
    end if;
  end process;

  -- this will run once and then wait for ever
  init : process
  begin
    -- time to tell LFSRs to load up some data
    load <= '1';
    -- and give it to them (to one of them, at least)
    -- initialization vectors
    q1 <= B"1010110010000011110";
    q2 <= B"0000010010111010001000";
    q3 <= B"10101110100000010011100";
    -- even though LFSRs are async, let's wait for a bit...
    wait until clock'event and clock = '0';
    -- ... and let them run freely
    load <= '0';
    -- this process is finished, make it wait ad infinitum
    wait;
  end process;

  -- okay, what's going on here? well, the 'clocker' process
  -- keeps running, changing clk -> NOT clk -> clk -> NOT clk ...
  -- and clk is fed to LFSRs, so they are busy working
  -- the simulation will continue until you kill it, or specify
  -- the stop time using '--stop-time=XXX' switch to ghdl

end complex;
