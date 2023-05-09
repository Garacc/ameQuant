import streamlit as st
import pickle
from tmp_yclass import yClass
import sys

# main function to run the app
def main():
    while True:
        # read data from stdin
        bytes = ""
        while True:
            input_str = sys.stdin.readline()
            if input_str.strip() == "":
                break
            bytes += input_str
        # bytes = sys.stdin.readline()
        y = pickle.loads(bytes.encode())
        
        # plot data using st.pyplot
        st.pyplot(y.data.plot(x="col1", y="col2"))

        # display info using st.write
        st.write(y.info)

        # create button A and B
        if st.button("A"):
            # return "A" to main program
            print("A")
        elif st.button("B"):
            # return "B" to main program
            print("B")
        else:
            print("111")


if __name__ == "__main__":
    main()
