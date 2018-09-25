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

playrandom: Java
	cd ReversiServer && java Reversi 10&
	cd ..
	cd ReversiRandom_Python && python3 RandomGuy.py localhost 1&
	cd ..
	cd ReversiRandom_Python && python3 RandomGuy.py localhost 2&
	cd ..

playtest: Java 
	cd ReversiServer && java Reversi 10&
	cd ..
	cd ReversiRandom_Python && python3 RandomGuy.py localhost 1&
	cd ..

kill:
	killall java
	killall python3
