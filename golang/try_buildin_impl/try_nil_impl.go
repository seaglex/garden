package main

import (
	"fmt"
	"time"
)
func reading(ch chan int) {
	for n:=0; n<10; n++ {
		var v int
		var ok bool
		select {
		case v, ok = <-ch:
			fmt.Println("read", v, ok, "from", ch)
		default:
			time.Sleep(time.Millisecond*10)
		}
	}
}
func main() {
	var slice []int64 = nil
	fmt.Println("slice-read", len(slice))
	var map1 map[int]int = nil
	{
		v, ok := map1[1]
		fmt.Println("map-read", v, ok)
		// map1[1] = 2 // runtime-error
	}
	var c1 chan int = nil
	go reading(c1)
	fmt.Println("chan-read")
	// c1 <- 2  // runtime-error
	time.Sleep(time.Second*1)
}
