#IMPORT simpsol.asl

#MACRO CALCPOINT
    CLA ; Clear alu, base and flags
    IMM8 BASE 00
    CGET H1
    AGET H1 ; Set acc = X
    CMPEQ ; Compare X == 0
    IMM8 ACC 00 ; Restore acc to 0
    JMPTO JZ ( CONCAT XIS0 #ARG1 )

    IMM8 BASE 02
    PC
        SUM
        DECCOUNT
        JPOS
    
    ; After multiplication loop ends
( CONCAT XIS0 #ARG1 ):
    ; Store ACC
    INCACC ; + 1
    MOVA #ARG1

    ; Inc X
    CGET H1
    INCCOUNT
    MOVC H1
#MACRO

; Calc f(x) = 2x + 1
; Stores this in H2, H3, H4
; Calc 3 points (starts in x = 0)

; X var
IMM8 H1 0 0

; CODE (is linear)
CALCPOINT H2
CALCPOINT H3
CALCPOINT H4
HALT
