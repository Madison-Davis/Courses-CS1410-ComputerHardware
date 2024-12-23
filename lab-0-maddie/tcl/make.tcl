create_project -force project_0 ./build/project_0 -part xc7a100tcsg324-1
add_files -norecurse [glob ./hdl/*.sv]
add_files -fileset constrs_1 -norecurse ./constraint/Nexys_A7.xdc
set_property top_file {./hdl/mux_top.sv} [current_fileset]
set_property top mux_top [current_fileset]
close_project
