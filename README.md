<h1>
    <img src='logo.png' align='right' width='49'> Sol-R1
</h1>

The objective of this CPU is a high clock and easy build
For example the ISA use only 4-bit mux and the connections is pretty simple

# CPU-Specs
- RISC FDE
- 8-bits CPU with paging 8-bits for 16-bits ADDR

# Recommended build
Clock 3 stages:
- clock-up  is the stage on the decoder works to prepare path
- clock-on  the signal clk of decoder is emited, this stage it can be small
- clock-off stage of the pc inc +1

Decoder:
- path-decoder gets the entry and active the path for make the instruction
- op-decoder   emit the signal CLK in components

# OBS
Idk inglesh, so if you read this and think im stupid, im not
