#IMPORT simpsol.asl

#MACRO CALCPOINT
    IMM8 BASE 0 2
    CGET H1
    PC ; Multiply 2 x times
        SUM
        DECCOUNT
        JPOS
    ; After multiplication loop ends
    INCACC ; + 1
    CGET H1
    INCCOUNT
    MOVC H1
    MOVA #ARG1
#MACRO

; Calc f(x) = 2x + 1
; Stores this in H2, H3, H4
; Calc 3 points (starts in x = 1)

; X var
IMM8 H1 0 0

; CODE (is linear)
CALCPOINT H2
CALCPOINT H3
CALCPOINT H4
HALT
