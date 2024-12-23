// Top module for synthesis on the FPGA
module mux_top
    (
        input logic [2:0] sw,
        output logic led
    );

    mux mux_unit (.a(sw[0]), .b(sw[1]), .sel(sw[2]), .f(led));
endmodule
