COMPILER = ifort

L = ../libs/ifort/
JSON_LIB = ../libs/json-fortran/ifort/
openmp = -qopenmp

$(L)qawafcp.so: qawafcp.f90 qawafcp_globals.o qawafcp_stack.o qawafcp_stack_frame.o qawafcp_history.o
	$(COMPILER) $(openmp) -shared -fpic qawafcp_globals.o qawafcp_stack.o qawafcp_stack_frame.o qawafcp_history.o qawafcp.f90 -o $(L)libqawafcp.so

qawafcp_globals.o: qawafcp_globals.f90 qawafcp_stack.o qawafcp_history.o
	$(COMPILER) $(openmp) -c -fpic qawafcp_globals.f90 -o qawafcp_globals.o -I$(JSON_LIB) -L$(JSON_LIB) $(JSON_LIB)libjsonfortran.a

qawafcp_stack.o: qawafcp_stack.f90 qawafcp_stack_frame.o
	$(COMPILER) $(openmp) -c -fpic qawafcp_stack.f90 -o qawafcp_stack.o

qawafcp_history.o: qawafcp_history.f90
	$(COMPILER) $(openmp) -c -fpic qawafcp_history.f90 -o qawafcp_history.o

qawafcp_stack_frame.o: qawafcp_stack_frame.f90
	$(COMPILER) $(openmp) -c -fpic qawafcp_stack_frame.f90 -o qawafcp_stack_frame.o



$(L)libqawafcp_globals.so: qawafcp_globals.f90 $(L)libqawafcp_stack.so $(L)libqawafcp_history.so
	$(COMPILER) $(openmp) -shared -fpic qawafcp_globals.f90 -o $(L)libqawafcp_globals.so

$(L)libqawafcp_stack_frame.so: qawafcp_stack_frame.f90
	$(COMPILER) $(openmp) -shared -fpic qawafcp_stack_frame.f90 -o $(L)libqawafcp_stack_frame.so

$(L)libqawafcp_stack.so: qawafcp_stack.f90 $(L)libqawafcp_stack_frame.so
	$(COMPILER) $(openmp) -shared -fpic qawafcp_stack.f90 -o $(L)libqawafcp_stack.so

$(L)libqawafcp_history.so: qawafcp_history.f90
	$(COMPILER) $(openmp) -shared -fpic qawafcp_history.f90 -o $(L)libqawafcp_history.so


.PHONY : clean
clean :
	rm -f *.so *.o *.mod
	rm -f $(L)*
