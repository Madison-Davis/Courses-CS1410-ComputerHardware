// The following module is made for SIMULATION ONLY - most of the language
// constructs used here will not synthesize, but will simulate
module mux_tb;
    // timeunit for the simulator waveform
    // delays (#1) are in units of nanoseconds with 2 decimal
    // places of accuracy
    timeunit 1ns/1ps;

    logic a, b, sel; // inputs
    logic f; // outputs

    // instantiate unit under test (uut)
    // somtimes this is also called the device under test (dut)
    mux uut (.a, .b, .sel, .f);

    initial begin
        for (int i = 0; i <= 4'b0111; i++) begin
            // set inputs
            a = i[0];
            b = i[1];
            sel = i[2];

            // wait 10 time units
            #10;

            // verify the output is correct
            if (sel && f !== b) begin
                $display("ERROR: a=%b, b=%b, sel=%b, f=%b", a, b, sel, f);
            end
            
            if (!sel && f !== a) begin
                $display("ERROR: a=%b, b=%b, sel=%b, f=%b", a, b, sel, f);
            end
        end

        $finish;
    end
endmodule
