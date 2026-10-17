; This is a basic asl lib

; Imediate helpers
#MACRO IMM8 ; REG, VALUE_HIGH, VALUE_LOW
    IMMH #ARG2
    IMML #ARG3
    IMM #ARG1
#MACRO