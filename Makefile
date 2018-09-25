all: Java

Java: clean Human Random Server

Human:
	cd ReversiHuman && javac Human.java && cd ..

Random:
	cd ReversiRandom_Java && javac RandomGuy.java && cd ..

Server:
	cd ReversiServer && javac Reversi.java && cd ..

clean: 
	cd ReversiHuman && rm -f *.class && cd ..
	cd ReversiRandom_Java && rm -f *.class && cd ..
	cd ReversiServer && rm -f *.class && cd ..

playrandom: playjava playrandomone playrandomtwo

playtest: playjava playrandomone 

playjava: Java
	cd ReversiServer && java Reversi 10 > ../server.out 2>&1 &
	cd ..

playrandomone:
	cd ReversiRandom_Python && python3 RandomGuy.py localhost 1 > ../randomone.out 2>&1 &
	cd ..

playrandomtwo:
	cd ReversiRandom_Python && python3 RandomGuy.py localhost 2 > ../randomtwo.out 2>&1 &
	cd ..

kill:
	killall -q java  || true
	killall -q python3 || true
	 
