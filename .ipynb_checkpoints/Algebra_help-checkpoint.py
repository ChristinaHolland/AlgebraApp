#!/usr/bin/env python
# coding: utf-8

# ### Functions for the app

# IMPORTS
import streamlit as st
import numpy as np
import re
import random
import pandas as pd

# FUNCTIONS


def replace_x(expression,substring,val):
    # This function replaces 'x' or any specified substring, with the string of a value
    expression = expression.replace('0'+substring,f'0*{val}')
    expression = expression.replace('1'+substring,f'1*{val}')
    expression = expression.replace('2'+substring,f'2*{val}')
    expression = expression.replace('3'+substring,f'3*{val}')
    expression = expression.replace('4'+substring,f'4*{val}')
    expression = expression.replace('5'+substring,f'5*{val}')
    expression = expression.replace('6'+substring,f'6*{val}')
    expression = expression.replace('7'+substring,f'7*{val}')
    expression = expression.replace('8'+substring,f'8*{val}')
    expression = expression.replace('9'+substring,f'9*{val}')
    expression = expression.replace('.'+substring,f'*{val}')
    expression = expression.replace(substring,    f'{val}')   
    return expression


def get_val(expression,val):
    # This function evaluates an algebraic expression of x (input as string) at a specified value
    # It calls the function "replace_x" which puts the value (as a string) into the expression,
    # then evaluates the string
    if '(' not in expression:
        # distribution not required
        expression = replace_x(expression,'x',val)
        return eval(expression)
    else:
        # distribution is required
        while '(' in expression:
            start = expression.index('(')
            end   = expression.index(')')
            # the part of the expression within the parentheses:
            mini_exp = expression[(start+1):end]
            mini_val = get_val(mini_exp,val)
            with_parens = expression[start:(end+1)]
            expression = replace_x(expression,with_parens,mini_val)
        # back to the entire expression
        expression = replace_x(expression,'x',val)
        return eval(expression)
    


def check_logic(prior, current):
    # This function compares two complete equations for logical equivalency
    #
    # remove all whitespace - this doesn't matter for checking logical consistency,
    # but does matter for checking for a solution where one side is just 'x'
    prior = prior.replace(' ','')
    current = current.replace(' ','')
    #
    # set up an array of test values - equations are all linear so we technically only need 2 test values
    # I set it to 21 in an abundance of caution, while still keeping the run time efficient
    check_vals = np.linspace(-10,10,21)
    # check that both equations are valid equations:
    chk0, solved, output_str = check_input_equation(prior)
    if chk0==False:
        output_str += ' [Error: prior line is not an equation]'
        return False, solved, output_str
    elif check_input_equation(current)==False:
        output_str += ' [Error: new line is not an equation]'
        return False, solved, output_str
    else:
        # split both equations into the left side and right side:
        prior = prior.split('=')
        current = current.split('=')
    # check all test values
    #
    # whether or not the test value makes either equation true, the discrepancy should stay the same - 
    # left - right for the 1st equation should equal left - right for the 2nd equation, so
    # (old_left - old_right) - (new_left - new_right) should equal zero or have a constant ratio for all test vals.
    chk_sum = []
    ratio = []
    for cv in check_vals:
        old_left  = get_val(prior[0],cv)
        old_right = get_val(prior[1],cv)
        new_left  = get_val(current[0],cv)
        new_right = get_val(current[1],cv)
        
        # print statements for debugging specific cases:
        #print(f'check_val = {cv}')
        #print(f'1st eqn: left = {old_left}, right = {old_right}, left - right = {old_left-old_right}')
        #print(f'2nd eqn: left = {new_left}, right = {new_right}, left - right = {new_left-new_right}')
        
        # round after 6 decimal places to prevent computational error from throwing false logical errors
        # + put in absolute value to account for user switching the left and right sides -- logically allowed.
        chk0 = np.abs(np.round(np.abs(old_left - old_right) - np.abs(new_left - new_right),6))
        chk_sum.append(chk0)
        # have to exclude the solution, if it is in the test set, to avoid dividing by zero:
        if np.abs(new_left - new_right)>0:
            ratio0=np.abs(np.round(np.abs(old_left - old_right) / np.abs(new_left - new_right),6))
            ratio.append(ratio0)
    # output
    output_old = output_str # string returned from checking the new equation
    chk_ratio = np.abs(np.round(max(ratio)-min(ratio),6))
    if (max(chk_sum)==0) or (chk_ratio==0):
        output_str = 'That step was correct'
        # is it solved?
        # If so, only one character from this string should show up: 'x', exactly once,
        # and one side or the other should be exactly equal to 'x'
        operations = '+-*()x'
        solvedx = sum([1 for c in current[0] if c in operations] + [1 for c in current[1] if c in operations])
        if (solvedx == 2) and ((current[0][0]=='-') or (current[1][0]=='-')):
            solvedx = 1
        if ((current[0]=='x') or (current[1]=='x')) and (solvedx==1):
            output_str += ', and you solved the equation!'
            return True, True, output_str
        elif solved==1:
            output_str += ' - ' + output_old
            return True, True, output_str
        else:
            output_str += '; keep it up!'
            return True, False, output_str
    else:
        output_str = "That's not quite correct. Try again."
        return False, False, output_str
    


def check_input_equation(equation):
    # This function is for when a user chooses to type in a starting equation, 
    # checks to see if is it valid and of the specified form.
    
    # initialize return variables:
    valid = False
    solved = False
    output_str = ''
    
    # is it even an equation?
    num_equal = len([m.start() for m in re.finditer('=', equation)])
    if num_equal != 1:
        output_str = 'Sorry, this is not a valid equation; please retype.'
        return valid, solved, output_str
    
    # check both sides now:
    sides = equation.split('=')

    #left side parentheses check - note that 'finditer' breaks when searching for parentheses, so do a replace first
    left = sides[0].replace('(','@@@@')
    left = left.replace(')','%%%%')
    num_open = len([m.start() for m in re.finditer('@@@@', left)])
    num_close= len([m.start() for m in re.finditer('%%%%', left)])
    if num_open != num_close:
        output_str = 'Your left side appears to have unmatched parentheses; please retype.'
        return valid, solved, output_str
    if num_open > 1:
        output_str = 'Sorry, at this time the app can only handle one distribution per side.'
        return valid, solved, output_str
    #right side parentheses check:
    right = sides[1].replace('(','@@@@')
    right = right.replace(')','%%%%')
    num_open = len([m.start() for m in re.finditer('@@@@', right)])
    num_close= len([m.start() for m in re.finditer('%%%%', right)])
    if num_open != num_close:
        output_str = 'Your right side appears to have unmatched parentheses; please retype.'
        return valid, solved, output_str
    if num_open > 1:
        output_str = 'Sorry, at this time the app can only handle one distribution per side.'
        return valid, solved, output_str
    
    # check that the equation uses only 'x':
    other_variables = 'abcdefghijklmnopqrstuvwyz'
    other_variables += other_variables.upper()
    if sum([1 for c in other_variables if c in equation])>0:
        output_str = 'Please retype your equation using "x" as your variable.'
        return valid, solved, output_str
    
    # if there is no variable, it can still be valid, at the end of the solving process:
    if 'x' not in equation:
        left = get_val(sides[0],0)
        right = get_val(sides[1],0)
        if  left != right:
            output_str = 'Your equation does not have a variable, and is false. (no solution)'
            valid = True
            solved = True
            return valid, solved, output_str
        else: 
            output_str = 'Your equation does not have a variable, and is true. (infinite solutions)'
            valid = True
            solved = True
            return valid, solved, output_str
    
    # if all checks passed:
    valid = True
    return valid, solved, output_str

# https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring



def make_equation(x_on_both, distribution, combining):
    
    # x_on_both is binary, distribution and combining are 0,1,2: 0 = neither side, 1 = one side, 2 = both sides
    
    # allowed coefficients:
    coefs = list(range(1,11))
    # choose random coefficients from this list:
    coefs = [random.choice(coefs) for n in range(10)]

    if x_on_both == 1:
    
        if combining == 2:
            if distribution == 2:
                # distribution and combining on both sides: (1024 cases)
                # ax + b + c(dx + f) = gx + h + i(jx + k)
                case = random.choice(list(range(1024)))
                if case//512       == 0: equation  = f'{coefs[0]}x'
                else:                    equation  = f' -{coefs[0]}x'
                if (case%512)//256 == 0: equation += f' +{coefs[1]}'
                else:                    equation += f' - {coefs[1]}'
                if (case%256)//128 == 0: equation += f' + {coefs[2]}('
                else:                    equation += f' - {coefs[2]}('
                if (case%128)//64  == 0: equation += f'{coefs[3]}x'
                else:                    equation += f'-{coefs[3]}x'
                if (case%64)//32   == 0: equation += f' + {coefs[4]}) ='
                else:                    equation += f' - {coefs[4]}) ='
                if (case%32)//16   == 0: equation += f' {coefs[5]}x'
                else:                    equation += f' -{coefs[5]}x'
                if (case%16)//8    == 0: equation += f' + {coefs[6]}'
                else:                    equation += f' - {coefs[6]}'
                if (case%8)//4     == 0: equation += f' + {coefs[7]}('
                else:                    equation += f' - {coefs[7]}('
                if (case%4)//2     == 0: equation += f'{coefs[8]}x'
                else:                    equation += f'-{coefs[8]}x'
                if case%2          == 0: equation += f' + {coefs[9]})'
                else:                    equation += f' - {coefs[9]})'
                
            elif distribution == 1:
                # distribution on one side and combining on both sides: (1024 cases)
                case = random.choice(list(range(1024)))
                if case//512 == 0:
                    # ax + b + cx + d = fx + g + h(jx + k)
                    if (case%512)//256 == 0: equation  = f'{coefs[0]}x'
                    else:                    equation  = f'-{coefs[0]}x'
                    if (case%256)//128 == 0: equation += f' + {coefs[1]}'
                    else:                    equation += f' - {coefs[1]}'
                    if (case%128)//64  == 0: equation += f' + {coefs[2]}x'
                    else:                    equation += f' - {coefs[2]}x'
                    if (case%64)//32   == 0: equation += f' + {coefs[3]} ='
                    else:                    equation += f' - {coefs[3]} ='
                    if (case%32)//16   == 0: equation += f' {coefs[4]}x'
                    else:                    equation += f' -{coefs[4]}x'
                    if (case%16)//8    == 0: equation += f' + {coefs[5]}'
                    else:                    equation += f' - {coefs[5]}'
                    if (case%8)//4     == 0: equation += f' + {coefs[6]}('
                    else:                    equation += f' - {coefs[6]}('
                    if (case%4)//2     == 0: equation += f' {coefs[7]}x'
                    else:                    equation += f' -{coefs[7]}x'
                    if case%2          == 0: equation += f' + {coefs[8]})'
                    else:                    equation += f' - {coefs[8]})'   
                else:
                    # ax + b + c(dx + f) = gx + h + jx + k    
                    if (case%512)//256 == 0: equation  = f'{coefs[0]}x'
                    else:                    equation  = f'-{coefs[0]}x'
                    if (case%256)//128 == 0: equation += f' + {coefs[1]}'
                    else:                    equation += f' - {coefs[1]}'
                    if (case%128)//64  == 0: equation += f' + {coefs[2]}('
                    else:                    equation += f' - {coefs[2]}('
                    if (case%64)//32   == 0: equation += f'{coefs[3]}x'
                    else:                    equation += f'-{coefs[3]}x'
                    if (case%32)//16   == 0: equation += f' + {coefs[4]}) ='
                    else:                    equation += f' - {coefs[4]}) ='
                    if (case%16)//8    == 0: equation += f' {coefs[5]}x'
                    else:                    equation += f' -{coefs[5]}x'
                    if (case%8)//4     == 0: equation += f' + {coefs[6]}'
                    else:                    equation += f' - {coefs[6]}'
                    if (case%4)//2     == 0: equation += f' + {coefs[7]}x'
                    else:                    equation += f' - {coefs[7]}x'
                    if case%2          == 0: equation += f' + {coefs[8]}'
                    else:                    equation += f' - {coefs[8]}'   
            else:
                # no distribution, combining on both sides:
                # ax + b + cx + d = fx + g + hx + j   (256 cases)
                case = random.choice(list(range(256)))
                if case//128 == 0:      equation = f'{coefs[0]}x'
                else:                   equation = f'-{coefs[0]}x'
                if (case%128)//64 == 0: equation += f' + {coefs[1]}'
                else:                   equation += f' - {coefs[1]}'
                if (case%64)//32  == 0: equation += f' + {coefs[2]}x'
                else:                   equation += f' - {coefs[2]}x'
                if (case%32)//16  == 0: equation += f' + {coefs[3]} ='
                else:                   equation += f' - {coefs[3]} ='
                if (case%16)//8   == 0: equation += f' {coefs[4]}x'
                else:                   equation += f' -{coefs[4]}x'
                if (case%8)//4    == 0: equation += f' + {coefs[5]}'
                else:                   equation += f' - {coefs[5]}'
                if (case%4)//2    == 0: equation += f' + {coefs[6]}x'
                else:                   equation += f' - {coefs[6]}x'
                if case%2         == 0: equation += f' + {coefs[7]}'
                else:                   equation += f' - {coefs[7]}'

        elif combining == 1:
            if distribution == 2:
                # distribution on both sides and combining on one side (512 cases)
                case = random.choice(list(range(512)))
                if case//256 == 0:
                    # ax + b + c(dx + f) = g(hx + j)
                    if (case%256)//128 == 0: equation  = f'{coefs[0]}x'
                    else:                    equation  = f'-{coefs[0]}x'
                    if (case%128)//64  == 0: equation += f' + {coefs[1]}'
                    else:                    equation += f' - {coefs[1]}'
                    if (case%64)//32   == 0: equation += f' + {coefs[2]}('
                    else:                    equation += f' - {coefs[2]}('
                    if (case%32)//16   == 0: equation += f'{coefs[3]}x'
                    else:                    equation += f'-{coefs[3]}x'
                    if (case%16)//8    == 0: equation += f' + {coefs[4]}) ='
                    else:                    equation += f' - {coefs[4]}) ='
                    if (case%8)//4     == 0: equation += f' {coefs[5]}('
                    else:                    equation += f' -{coefs[5]}('
                    if (case%4)//2     == 0: equation += f'{coefs[6]}x'
                    else:                    equation += f'-{coefs[6]}x'
                    if case%2          == 0: equation += f' + {coefs[7]})'
                    else:                    equation += f' - {coefs[7]})'
                else:
                    # a(bx + c) = dx + f + g(hx + j)  
                    if (case%256)//128 == 0: equation  = f'{coefs[0]}('
                    else:                    equation  = f'-{coefs[0]}('
                    if (case%128)//64  == 0: equation += f'{coefs[1]}x'
                    else:                    equation += f'-{coefs[1]}x'
                    if (case%64)//32   == 0: equation += f' + {coefs[2]}) ='
                    else:                    equation += f' - {coefs[2]}) ='
                    if (case%32)//16   == 0: equation += f' {coefs[3]}x'
                    else:                    equation += f' -{coefs[3]}x'
                    if (case%16)//8    == 0: equation += f' + {coefs[4]}'
                    else:                    equation += f' - {coefs[4]}'
                    if (case%8)//4     == 0: equation += f' + {coefs[5]}('
                    else:                    equation += f' - {coefs[5]}('
                    if (case%4)//2     == 0: equation += f'{coefs[6]}x'
                    else:                    equation += f'-{coefs[6]}x'
                    if case%2          == 0: equation += f' + {coefs[7]})'
                    else:                    equation += f' - {coefs[7]})'

                    
            elif distribution == 1:
                # distribution on one side and combining on one side (512 cases)
                case = random.choice(list(range(512)))
                if case//128 == 0:
                    # ax + b + c(dx + f) = gx + h    
                    if (case%128)//64== 0: equation  = f'{coefs[0]}x'
                    else:                  equation  = f'-{coefs[0]}x'
                    if (case%64)//32 == 0: equation += f' + {coefs[1]}'
                    else:                  equation += f' - {coefs[1]}'
                    if (case%32)//16 == 0: equation += f' + {coefs[2]}('
                    else:                  equation += f' - {coefs[2]}('
                    if (case%16)//8  == 0: equation += f'{coefs[3]}x'
                    else:                  equation += f'-{coefs[3]}x'
                    if (case%8)//4   == 0: equation += f' + {coefs[4]}) ='
                    else:                  equation += f' - {coefs[4]}) ='
                    if (case%4)//2   == 0: equation += f' {coefs[5]}x'
                    else:                  equation += f' -{coefs[5]}x'
                    if case%2        == 0: equation += f' + {coefs[6]}'
                    else:                  equation += f' - {coefs[6]}'   
                elif case//128 == 1:
                    # ax + b = cx + d + f(gx + h)    
                    if (case%128)//64== 0: equation  = f'{coefs[0]}x'
                    else:                  equation  = f'-{coefs[0]}x'
                    if (case%64)//32 == 0: equation += f' + {coefs[1]} ='
                    else:                  equation += f' - {coefs[1]} ='
                    if (case%32)//16 == 0: equation += f'{coefs[2]}x'
                    else:                  equation += f'-{coefs[2]}x'
                    if (case%16)//8  == 0: equation += f' + {coefs[3]}'
                    else:                  equation += f' - {coefs[3]}'
                    if (case%8)//4   == 0: equation += f' + {coefs[4]}('
                    else:                  equation += f' - {coefs[4]}('
                    if (case%4)//2   == 0: equation += f'{coefs[5]}x'
                    else:                  equation += f'-{coefs[5]}x'
                    if case%2        == 0: equation += f' + {coefs[6]})'
                    else:                  equation += f' - {coefs[6]})'
                elif case//128 == 2:
                    # ax + b + cx + d = f(gx + h)    
                    if (case%128)//64== 0: equation  = f'{coefs[0]}x'
                    else:                  equation  = f'-{coefs[0]}x'
                    if (case%64)//32 == 0: equation += f'+{coefs[1]}'
                    else:                  equation += f' - {coefs[1]}'
                    if (case%32)//16 == 0: equation += f' + {coefs[2]}x'
                    else:                  equation += f' - {coefs[2]}x'
                    if (case%16)//8  == 0: equation += f' + {coefs[3]} ='
                    else:                  equation += f' - {coefs[3]} ='
                    if (case%8)//4   == 0: equation += f' {coefs[4]}('
                    else:                  equation += f' -{coefs[4]}('
                    if (case%4)//2   == 0: equation += f'{coefs[5]}x'
                    else:                  equation += f'-{coefs[5]}x'
                    if case%2        == 0: equation += f' + {coefs[6]})'
                    else:                  equation += f' - {coefs[6]})'
                else:
                    # a(bx + c) = dx + f + gx + h    
                    if (case%128)//64== 0: equation  = f'{coefs[0]}('
                    else:                  equation  = f'-{coefs[0]}('
                    if (case%64)//32 == 0: equation += f'{coefs[1]}x'
                    else:                  equation += f'-{coefs[1]}x'
                    if (case%32)//16 == 0: equation += f' + {coefs[2]}) ='
                    else:                  equation += f' - {coefs[2]}) ='
                    if (case%16)//8  == 0: equation += f' {coefs[3]}x'
                    else:                  equation += f' -{coefs[3]}x'
                    if (case%8)//4   == 0: equation += f' + {coefs[4]}'
                    else:                  equation += f' - {coefs[4]}'
                    if (case%4)//2   == 0: equation += f' + {coefs[5]}x'
                    else:                  equation += f' - {coefs[5]}x'
                    if case%2        == 0: equation += f' + {coefs[6]}'
                    else:                  equation += f' - {coefs[6]}'

            else:
                # no distribution, combining on one side:
                # ax + b = cx + d + fx + g OR ax + b + fx + g = cx + d (128 cases)
                case = random.choice(list(range(128)))
                if (case%64)//32 == 0: equation  = f'{coefs[0]}x'               
                else:                  equation  = f'-{coefs[0]}x'
                if (case%32)//16 == 0: equation += f' + {coefs[1]}'
                else:                  equation += f' - {coefs[1]}'
                if case//64 == 0:
                    if (case%16)//8 == 0: equation += f' = {coefs[2]}x'
                    else:                 equation += f' = -{coefs[2]}x'
                    if (case%8)//4  == 0: equation += f' + {coefs[3]}'
                    else:                 equation += f' - {coefs[3]}'
                    if (case%4)//2  == 0: equation += f' + {coefs[4]}x'
                    else:                 equation += f' - {coefs[4]}x'
                else:
                    if (case%16)//8 == 0: equation += f' + {coefs[2]}x'
                    else:                 equation += f' - {coefs[2]}x'
                    if (case%8)//4  == 0: equation += f' + {coefs[3]} ='
                    else:                 equation += f' - {coefs[3]} ='
                    if (case%4)//2  == 0: equation += f' {coefs[4]}x'
                    else:                 equation += f' -{coefs[4]}x'
                if case%2       == 0: equation += f' + {coefs[5]}'
                else:                 equation += f' - {coefs[5]}'
    
        else:
            if distribution == 2:
                # distribution on both sides, no combining: c(dx + f) = i(jx + k) (64 cases with + or - coefs)
                case = random.choice(list(range(64)))
                if case//32      == 0: equation  = f'{coefs[0]}('
                else:                  equation  = f'-{coefs[0]}('
                if (case%32)//16 == 0: equation += f'{coefs[1]}x'
                else:                  equation += f'-{coefs[1]}x'
                if (case%16)//8  == 0: equation += f' + {coefs[2]}) ='
                else:                  equation += f' - {coefs[2]}) ='
                if (case%8)//4   == 0: equation += f' {coefs[3]}('
                else:                  equation += f' -{coefs[3]}('
                if (case%4)//2   == 0: equation += f'{coefs[4]}x'
                else:                  equation += f'-{coefs[4]}x'
                if case%2        == 0: equation += f' + {coefs[5]})'
                else:                  equation += f' - {coefs[5]})'
            elif distribution == 1:
                # distribution on one side, no combining:
                # c(dx + f) = gx + h   OR ax + b = i(jx + k) (64 cases with pos or neg coefs)
                case = random.choice(list(range(64)))
                if case//32 == 0:
                    if (case%32)//16 == 0: equation  = f'{coefs[0]}('
                    else:                  equation  = f'-{coefs[0]}('
                    if (case%16)//8  == 0: equation += f'{coefs[1]}x'
                    else:                  equation += f'-{coefs[1]}x'
                    if (case%8)//4   == 0: equation += f' + {coefs[2]}) ='
                    else:                  equation += f' - {coefs[2]}) ='
                    if (case%4)//2   == 0: equation += f' {coefs[3]}x'
                    else:                  equation += f' -{coefs[3]}x'
                    if case%2        == 0: equation += f' + {coefs[4]}'
                    else:                  equation += f' - {coefs[4]}'
                else:
                    if (case%32)//16 == 0: equation  = f'{coefs[0]}x'
                    else:                  equation  = f'-{coefs[0]}x'
                    if (case%16)//8  == 0: equation += f' + {coefs[1]} ='
                    else:                  equation += f' - {coefs[1]} ='
                    if (case%8)//4   == 0: equation += f' {coefs[2]}('
                    else:                  equation += f' -{coefs[2]}('
                    if (case%4)//2   == 0: equation += f'{coefs[3]}x'
                    else:                  equation += f'-{coefs[3]}x'
                    if case%2        == 0: equation += f' + {coefs[4]})'
                    else:                  equation += f' - {coefs[4]})'                    
            else:
                # no distribution, no combining, but x on both sides: ax+b=cx+d, coefs can be pos or neg (16 cases)
                case = random.choice(list(range(16)))
                if case//8 == 0:     equation  = f'{coefs[0]}x'
                else:                equation  = f'-{coefs[0]}x'
                if (case%8)//4 == 0: equation += f' + {coefs[1]} ='
                else:                equation += f' - {coefs[1]} ='
                if (case%4)//2 == 0: equation += f' {coefs[2]}x'
                else:                equation += f' -{coefs[2]}x'
                if case%2      == 0: equation += f' + {coefs[3]}'
                else:                equation += f' - {coefs[3]}'
                
                
    
    else:       
        # x on only one side: ax + b = c OR a = bx + c, and a,b,c can be pos or neg (16 cases)
        case = random.choice(list(range(16))) 
        if case//8 == 0:
                if (case%8)//4 == 0: equation  = f'{coefs[0]}x'
                else:                equation  = f'-{coefs[0]}x'
                if (case%4)//2 == 0: equation += f' + {coefs[1]} ='
                else:                equation += f' - {coefs[1]} ='
                if case%2      == 0: equation += f' {coefs[2]}'
                else:                equation += f' -{coefs[2]}'            
        else:
                if (case%8)//4 == 0: equation  = f'{coefs[0]} ='
                else:                equation  = f'-{coefs[0]} ='
                if (case%4)//2 == 0: equation += f' {coefs[1]}x'
                else:                equation += f' -{coefs[1]}x'
                if case%2      == 0: equation += f' + {coefs[2]}'
                else:                equation += f' - {coefs[2]}'            

    return equation
    
def get_example(equation0):
    # This function returns one of five examples to be displayed, depending on the type of linear equation chosen.
    if sum([1 for c in equation0 if c=='x'])==1:
        # x on only one side
        example_txt = ['4x + 3 = 15']
        example_txt.append('SUBTRACT 3 FROM BOTH SIDES')
        example_txt.append('4x = 12')
        example_txt.append('DIVIDE BOTH SIDES BY 4')
        example_txt.append('THE SOLUTION IS:')
        example_txt.append('x = 3')
    else:
        if sum([1 for c in equation0 if c=='('])>0:
            if sum([1 for c in equation0 if c=='x'])>2:
                # both distribution and combining like terms
                example_txt = ['4x + 3 + 2(x - 5) = -2x - 4 + 5(3x + 2)']
                example_txt.append('DISTRUBUTE INTO EACH PARENTHESIS')
                example_txt.append('4x + 3 + 2x - 10 = -2x - 4 + 15x + 10')
                example_txt.append('COMBINE LIKE TERMS')
                example_txt.append('6x - 7 = 13x + 6')
                example_txt.append('ADD 7 TO BOTH SIDES')
                example_txt.append('6x = 13x + 13')
                example_txt.append('SUBTRACT 13x FROM BOTH SIDES')
                example_txt.append('-7x = 13')
                example_txt.append('DIVIDE BOTH SIDES BY -7')
                example_txt.append('THE SOLUTION IS:')
                example_txt.append('x = -13/7')
            else:
                # distribution, but no need to combine like terms
                example_txt = ['2(x - 4) = 5(2x + 4)']
                example_txt.append('DISTRUBUTE INTO EACH PARENTHESIS')
                example_txt.append('2x - 8 = 10x + 20')
                example_txt.append('SUBTRACT 10x FROM BOTH SIDES')
                example_txt.append('-8x - 8 = 20')
                example_txt.append('ADD 8 TO BOTH SIDES')
                example_txt.append('-8x = 28')
                example_txt.append('DIVIDE BOTH SIDES BY -8')
                example_txt.append('THE SOLUTION IS:')
                example_txt.append('x = -7/2 OR x = -3.5')
        else:
            if sum([1 for c in equation0 if c=='x'])>2:
                # combining like terms but no distribution
                example_txt = ['4x + 3 + 2x - 5 = -2x - 4 + 5x + 11']
                example_txt.append('COMBINE LIKE TERMS')
                example_txt.append('6x - 2 = 3x + 7')
                example_txt.append('SUBTRACT 3x FROM BOTH SIDES')
                example_txt.append('3x - 2 = 7')
                example_txt.append('ADD 2 TO BOTH SIDES')
                example_txt.append('3x = 9')
                example_txt.append('DIVIDE BOTH SIDES BY 3')
                example_txt.append('THE SOLUTION IS:')
                example_txt.append('x = 3')
            else:
                # x on both sides but no distribution, no combining like terms
                example_txt = ['5x - 8 = 2x + 16']
                example_txt.append('SUBTRACT 2x FROM BOTH SIDES')
                example_txt.append('3x - 8 = 16')
                example_txt.append('ADD 8 TO BOTH SIDES')
                example_txt.append('3x = 24')
                example_txt.append('DIVIDE BOTH SIDES BY 3')
                example_txt.append('THE SOLUTION IS:')
                example_txt.append('x = 8')
    return example_txt

def get_equation():
    # This function is called to get the equation the student wants to practice (linear equations)
    equation0 = 'Unknown; please select an equation'

    in0 = st.sidebar.selectbox('What do you want to do?', ['Type in an equation','See a random practice equation'])

    if in0 == 'Type in an equation':
        # They will type in an equation:
        st.sidebar.write('Please note that equations must use "x" as the variable, and this beta version of the app does not yet support quadratic, polynomial, radical or rational equations: linear only. Thank you.')
        st.sidebar.write('')
        equation0 = st.sidebar.text_input('Please type in your equation:')
        valid, solved, output_str = check_input_equation(equation0)
        st.sidebar.write(output_str)
        # don't display an example until the input equation has been checked and deemed valid
        if valid == True:
            # give example
            st.sidebar.write('HERE IS A SIMILAR EXAMPLE:')
            example_txt = get_example(equation0)
            for txt in example_txt:
                st.sidebar.write(txt.lower())
    else:
        # They want a randomly generated equation (which they will need to copy/paste into the typing space)
        # First, choose type:
        in1 = st.sidebar.selectbox('Select level:', ['x on one side','x on both sides'])
        if in1 == 'x on both sides':
            # only ask about distribution and combining like terms if they choose x on both sides
            x_onboth = 1
            in2 = st.sidebar.selectbox('Distribution required:',['None', 'On only one side', 'On both sides'])
            if in2 == 'None': distr = 0
            elif in2 == 'On only one side': distr = 1
            else: distr = 2
            in3 = st.sidebar.selectbox('Combining terms required:',['None', 'On only one side', 'On both sides'])
            if in3 == 'None': comb = 0
            elif in3 == 'On only one side': comb = 1
            else: comb = 2
        else:
            x_onboth = 0
            distr = 0
            comb = 0
        # get the equation:
        equation0 = make_equation(x_onboth, distr, comb)
        st.sidebar.write(equation0)
        st.sidebar.write('Unfortunately streamlit completely refreshes at every step. To use this equation,')
        st.sidebar.write('please copy it, select "Type in an equation" above, and paste it in.')
        st.sidebar.write('If you want a different equation, hit refresh or change your options above.')
        valid = True

    return equation0,in0
    
def diagnose(equation):
    # This function returns a hint based on the type of equation, if the student missed a step
    if sum([1 for c in equation if c=='x'])==1: # if there is only one x
        diagnosis = 'Try adding or subtracting, and then dividing.'
    else:
        if sum([1 for c in equation if c=='('])>0: # there is distribution
            if sum([1 for c in equation if c=='x'])>2: # there is combining like terms
                diagnosis = 'Try distributing, then combining like terms.'
            else: # there is no combining like terms, but there is still distribution
                diagnosis = 'Try distributing.'
        else: # there is no distribution
            if sum([1 for c in equation if c=='x'])>2: # there is combining like terms
                diagnosis = 'Try combining like terms.'
            else: # no distribution and no combining like terms
                diagnosis = 'Try adding or subtracting, and then dividing.'
    return diagnosis

def decimal_to_fraction(chk):
    # This function returns a simplified fraction for an input decimal value
    num_range = list(range(1,201))
    nums = [n for n in num_range for d in num_range]
    dens = [d for n in num_range for d in num_range]
    decimals= [n/d for n in num_range for d in num_range]
    selected = [j for j,c in enumerate(decimals) if np.round(np.abs(chk-c),6)==0]
    if len(selected)<1:
        return None, None
    else:
        m = selected[0]
        numer = nums[m]
        denom = dens[m]        
        return numer, denom

def combine_string(start):
    
    # takes in a string that might be something like "-2 + 3/4", evaluates it and turns it back into a fraction if needed.
    
    chk = eval(start) # get the numerical value of the string
    if chk<0: # negative
        sign = -1
        chk = np.abs(chk)
    else: # positive
        sign = 1
    numer, denom = decimal_to_fraction(chk) # get it as a fraction
    numer = sign*numer
    
    if denom!=1: # if it is actually a fraction
        if numer<denom:
            new_string = f'{numer}/{denom}' # fraction
        else:
            new_string = f'{numer//denom} {numer%denom}/{denom}' # improper fraction changed to a mixed number
    else: # if it is a whole number
        new_string = f'{numer}'
    
    return new_string

   
def simplify_radical(start):
    # This function takes in a number from under a square root, and simplifes the radical
    # for instance simplify_radical(20) --> 2,5,1, because sqrt(20) = 2 sqrt(5) / 1
    # simplify_radical(8/5) --> 2,10,5, because sqrt(8/5) = sqrt(40/25) = 2 sqrt(10)/5
    
    # get list of perfect squares to check against, largest first
    perf_squares = [c*c for c in list(range(100,0,-1))]
    num_range = list(range(1,201))
    
    chk = start%1
    
    if chk != 0: # decimal value -- convert remainder to fraction
        chk, start_denom = decimal_to_fraction(chk)
        if chk==None:
            return None, None, None
    else:
        start_denom = 1
    
    start_num = (start//1)*start_denom + chk # complete fraction
        
    if start_denom not in perf_squares: # make there be a perfect square in the denominator, to avoid radicals in the denominator
        start_num = start_num*start_denom
        start_denom = start_denom*start_denom

    denom = np.round(np.power(start_denom,0.5)) # since the denominator is now a perfect square, take the square root
    squares = [s for s in perf_squares if start_num%s==0] # find the largest perfect square that is a factor of the numerator
    in_rad = start_num// squares[0] # what is left in the radical
    out_rad= np.power(squares[0],0.5) # take the square root of that perfect square out of the radical
    
    ## SQRT({start}) = {out_rad}SQRT({in_rad})/{denom}
    
    out_rad = int(out_rad)
    in_rad = int(in_rad)
    denom = int(denom)
    out_rad, denom = simplify_fraction(out_rad,denom) # simplify the fraction outside the radical if needed
    
    return out_rad, in_rad, denom


def simplify_fraction(n0, d0):
    
    # simplifies the fraction n0/d0, if possible
    
    chk = n0/d0
    sign = (chk/np.abs(chk))
    n0 = np.abs(n0)
    d0 = np.abs(d0)
    
    m = max([n0, d0])
    common_factors = [j for j in range(2,(m+1)) if (n0%j==0) and (d0%j==0)]
    if len(common_factors)<1: # no common factors, cannot be simplified, leave it alone
        n1 = int(sign*n0)
        d1 = d0
    else: # at least one common factor > 1, divide numerator and denominator by the greatest common factor
        gcf = max(common_factors)
        n1 = int(sign*n0/gcf)
        d1 = int(d0/gcf)
    
    return n1, d1

def synthetic_division(c5,c4,c3,c2,c1,c0,r):
    # returns the coeficients ot the result of doing synthetic division on {c5}x^5+{c4}x^4+{c3}x^3+{c2}x^2+{c1}x+{c0} by x-r for root r
    b5 = int(c5)
    b4 = int(c4 + b5*r)
    b3 = int(c3 + b4*r)
    b2 = int(c2 + b3*r)
    b1 = int(c1 + b2*r)
    b0 = int(c0 + b1*r)
    if r%1!=0:
        n,d = decimal_to_fraction(r)
        b5 = int(b5/d)
        b4 = int(b4/d)
        b3 = int(b3/d)
        b2 = int(b2/d)
        b1 = int(b1/d)
        b0 = int(b0/d)
    return b5, b4, b3, b2, b1, b0
    # result is {b5}x^4 + {b4}x^3 + {b3}x^2 + {b2}x + {b1} + {b0}/(x-r)
    
# APP CODE:


# SIDEBAR:

eqn_type = st.sidebar.selectbox('What do you need to practice today?', ['Linear Equations', 'Quadratic Equations', 'Polynomial Equations'])

# MAIN PAGE:

st.title('Help with Algebra, Line by Line')

st.header('Welcome!')

st.write('New equations can be set using the side bar.')

############################################### LINEAR EQUATIONS SECTION ###############################################
if eqn_type == 'Linear Equations':
    

    # Get the equation via user input (on the sidebar)
    equation0,in0 = get_equation()
    if in0=='Type in an equation':

        # first step:
        cnt = 1
        message0 = f'[{cnt-1}]: the equation is:  ' + equation0
        st.write(message0)
        message1 = f'Please type the equation after step {cnt}: '
        line1 = st.text_input(message1, value=equation0)
        if line1 != equation0:
            valid, solved, output = check_logic(equation0, line1)
            if valid == 0: # logic error
                diagnosis = diagnose(equation0)
                st.write(output + ' ' + diagnosis)
            else:
                if solved == 1: # solved it!
                    st.write('Great job!')
                    st.write(output)
                    st.balloons()
                else: # need to continue
                    st.write(output)

                    cnt += 1 # 2ND STEP
                    message0 = f'[{cnt-1}]: the equation is:  ' + line1
                    st.write(message0)
                    message1 = f'Please type the equation after step {cnt}: '
                    linenew = st.text_input(message1, value=line1)
                    if linenew != line1:
                        valid, solved, output = check_logic(line1, linenew)
                        if valid == 0: # logic error
                            diagnosis = diagnose(line1)
                            st.write(output + ' ' + diagnosis)
                        else: # valid, check for solved
                            if solved == 1: # solved it!
                                st.write('Great job!')
                                st.write(output)
                                st.balloons()
                            else: # need to continue
                                st.write(output)
                                line1 = linenew

                                cnt += 1 # 3RD STEP
                                message0 = f'[{cnt-1}]: the equation is:  ' + line1
                                st.write(message0)
                                message1 = f'Please type the equation after step {cnt}: '
                                linenew = st.text_input(message1, value=line1)
                                if linenew != line1:
                                    valid, solved, output = check_logic(line1, linenew)
                                    if valid == 0: # logic error
                                        diagnosis = diagnose(line1)
                                        st.write(output + ' ' + diagnosis)
                                    else: # valid, check for solved
                                        if solved == 1: # solved it!
                                            st.write('Great job!')
                                            st.write(output)
                                            st.balloons()
                                        else: # need to continue
                                            st.write(output)
                                            line1 = linenew

                                            cnt += 1 # 4TH STEP
                                            message0 = f'[{cnt-1}]: the equation is:  ' + line1
                                            st.write(message0)
                                            message1 = f'Please type the equation after step {cnt}: '
                                            linenew = st.text_input(message1, value=line1)
                                            if linenew != line1:
                                                valid, solved, output = check_logic(line1, linenew)
                                                if valid == 0: # logic error
                                                    diagnosis = diagnose(line1)
                                                    st.write(output + ' ' + diagnosis)
                                                else: # valid, check for solved
                                                    if solved == 1: # solved it!
                                                        st.write('Great job!')
                                                        st.write(output)
                                                        st.balloons()
                                                    else: # need to continue
                                                        st.write(output)
                                                        line1 = linenew

                                                        cnt += 1 # 5TH STEP
                                                        message0 = f'[{cnt-1}]: the equation is:  ' + line1
                                                        st.write(message0)
                                                        message1 = f'Please type the equation after step {cnt}: '
                                                        linenew = st.text_input(message1, value=line1)
                                                        if linenew != line1:
                                                            valid, solved, output = check_logic(line1, linenew)
                                                            if valid == 0: # logic error
                                                                diagnosis = diagnose(line1)
                                                                st.write(output + ' ' + diagnosis)
                                                            else: # valid, check for solved
                                                                if solved == 1: # solved it!
                                                                    st.write('Great job!')
                                                                    st.write(output)
                                                                    st.balloons()
                                                                else: # need to continue
                                                                    st.write(output)
                                                                    line1 = linenew

                                                                    cnt += 1 # 6TH STEP
                                                                    message0 = f'[{cnt-1}]: the equation is:  ' + line1
                                                                    st.write(message0)
                                                                    message1 = f'Please type the equation after step {cnt}: '
                                                                    linenew = st.text_input(message1, value=line1)
                                                                    if linenew != line1:
                                                                        valid, solved, output = check_logic(line1, linenew)
                                                                        if valid == 0: # logic error
                                                                            diagnosis = diagnose(line1)
                                                                            st.write(output + ' ' + diagnosis)
                                                                        else: # valid, check for solved
                                                                            if solved == 1: # solved it!
                                                                                st.write('Great job!')
                                                                                st.write(output)
                                                                                st.balloons()
                                                                            else: # need to continue
                                                                                st.write(output)
                                                                                line1 = linenew

                                                                                cnt += 1 # 7TH STEP
                                                                                message0 = f'[{cnt-1}]: the equation is:  ' + line1
                                                                                st.write(message0)
                                                                                message1 = f'Please type the equation after step {cnt}: '
                                                                                linenew = st.text_input(message1, value=line1)
                                                                                if linenew != line1:
                                                                                    valid, solved, output = check_logic(line1, linenew)
                                                                                    if valid == 0: # logic error
                                                                                        diagnosis = diagnose(line1)
                                                                                        st.write(output + ' ' + diagnosis)
                                                                                    else: # valid, check for solved
                                                                                        if solved == 1: # solved it!
                                                                                            st.write('Great job!')
                                                                                            st.write(output)
                                                                                            st.balloons()
                                                                                        else: # need to continue
                                                                                            st.write(output)
                                                                                            line1 = linenew

                                                                                            cnt += 1 # 8TH STEP
                                                                                            message0 = f'[{cnt-1}]: the equation is:  ' + line1
                                                                                            st.write(message0)
                                                                                            message1 = f'Please type the equation after step {cnt}: '
                                                                                            linenew = st.text_input(message1, value=line1)
                                                                                            if linenew != line1:
                                                                                                valid, solved, output = check_logic(line1, linenew)
                                                                                                if valid == 0: # logic error
                                                                                                    diagnosis = diagnose(line1)
                                                                                                    st.write(output + ' ' + diagnosis)
                                                                                                else: # valid, check for solved
                                                                                                    if solved == 1: # solved it!
                                                                                                        st.write('Great job!')
                                                                                                        st.write(output)
                                                                                                        st.balloons()
                                                                                                    else: # need to continue
                                                                                                        st.write(output)
                                                                                                        line1 = linenew

                                                                                                        cnt += 1 # 9TH STEP
                                                                                                        message0 = f'[{cnt-1}]: the equation is:  ' + line1
                                                                                                        st.write(message0)
                                                                                                        message1 = f'Please type the equation after step {cnt}: '
                                                                                                        linenew = st.text_input(message1, value=line1)
                                                                                                        if linenew != line1:
                                                                                                            valid, solved, output = check_logic(line1, linenew)
                                                                                                            if valid == 0: # logic error
                                                                                                                diagnosis = diagnose(line1)
                                                                                                                st.write(output + ' ' + diagnosis)
                                                                                                            else: # valid, check for solved
                                                                                                                if solved == 1: # solved it!
                                                                                                                    st.write('Great job!')
                                                                                                                    st.write(output)
                                                                                                                    st.balloons()
                                                                                                                else: # need to continue
                                                                                                                    st.write(output)
                                                                                                                    line1 = linenew

                                                                                                                    cnt += 1 # 10TH STEP
                                                                                                                    message0 = f'[{cnt-1}]: the equation is:  ' + line1
                                                                                                                    st.write(message0)
                                                                                                                    message1 = f'Please type the equation after step {cnt}: '
                                                                                                                    linenew = st.text_input(message1, value=line1)
                                                                                                                    if linenew != line1:
                                                                                                                        valid, solved, output = check_logic(line1, linenew)
                                                                                                                        if valid == 0: # logic error
                                                                                                                            diagnosis = diagnose(line1)
                                                                                                                            st.write(output + ' ' + diagnosis)
                                                                                                                        else: # valid, check for solved
                                                                                                                            if solved == 1: # solved it!
                                                                                                                                st.write('Great job!')
                                                                                                                                st.write(output)
                                                                                                                                st.balloons()
                                                                                                                            else: # need to continue, but stuck
                                                                                                                                st.write(output)
                                                                                                                                line1 = linenew

                                                                                                                                st.write('You seem to be having trouble.')
                                                                                                                                st.write('This problem should not take this many steps -- go back up and check your work.')

                                                                                                                                
############################################### QUADRATIC EQUATIONS SECTION ###############################################

elif eqn_type == 'Quadratic Equations':

    Q1 = st.sidebar.selectbox('What form of equation to start?',['Standard', 'Factored', 'Vertex'])
    
############################################### EQUATION IN STANDARD FORM ###############################################
    if Q1 == 'Standard':
        coef_options  = list(range(-10,11))
        coef_options2 = list(range(-20,21))
        a = st.sidebar.selectbox('Enter "a" (the quadratic coefficient):',coef_options)
        b = st.sidebar.selectbox('Enter "b" (the linear coefficient):',coef_options)
        c = st.sidebar.selectbox('Enter "c" (the constant term):',coef_options2)
        if a == 1:
            disp_a = 'x^2'
        else:
            disp_a = f'{a}x^2'
        equation0 = disp_a + f' + {b}x + {c} = 0'
        st.latex(equation0)
        
        slv_mthd = st.selectbox('Which method would you like to practice?', ['Factoring', 'Completing the square', 'Quadratic Formula'])
        
        if slv_mthd == 'Factoring':
        ############################################### SOLVE BY FACTORING ###############################################

            if a<0:
                factorlist = [c for c in coef_options if c<0]
            else:
                factorlist = [c for c in coef_options if c>0]
            
            if (c==0) and (b==0): # trivial case of ax^2 = 0
                st.write(f'Since b = 0 and c = 0, we just have ${a}x^2 = 0$.')
                st.write("You don't even need to factor this, actually. What is always the solution, when you have $ax^n = 0$?")
                soln1_in = st.selectbox('Solution: ',['SELECT'] + coef_options)
                if soln1_in != 0:
                    st.write('Try again.')
                elif soln1_in ==0:
                    st.write('Great job; you solved it!')
                    st.balloons()
               

            elif c==0: # GCF case of ax^2 + bx = 0
                common = [f for f in factorlist if (a%f==0) and (b%f==0)] # find the gcf
                if len(common)>0: gcf = max(common)
                else: gcf = 1
                st.write('It looks like c = 0, so you can factor this with a simple GCF')
                gcf_in = st.selectbox('How many x can you take out in the GCF?',['SELECT'] + coef_options)
                if (gcf_in!=gcf):
                    st.write('Not quite. Try again.')
                elif gcf_in==gcf:
                    st.write('Great job!')
                    if b>0:    equation1 = f'{gcf}x({a//gcf}x + {b//gcf})' # new equation with {gcf}x factored out
                    else:      equation1 = f'{gcf}x({a//gcf}x - {-1*b//gcf})'
                    st.write(equation1)
                    st.write(f'One equation is {gcf}x = 0. What is the solution to that equation?')
                    soln1_in = st.selectbox('Solution: ',['SELECT'] + coef_options)
                    if soln1_in != 0: # solution to {gcf}x = 0 is always x = 0
                        st.write('Try again.')
                    elif soln1_in ==0:
                        st.write('Great job; now what is the other equation?')
                        factor_eqn1 = f'{a//gcf}x + {b//gcf} = 0'
                        if b < 0: factor_eqn1 = factor_eqn1.replace(f'+ {b//gcf}', f'- {-1*b//gcf}') # make it look prettier x - {} instead of x + -{}
                        f_eqn1_in = st.selectbox('Which of these equations should you solve?',['SELECT', factor_eqn1.replace('-','+'), factor_eqn1.replace('+','-')])
                        if (f_eqn1_in!=factor_eqn1):
                            st.write('Try again. Hint: The factors should be set equal to zero because anything multiplied by zero is zero.')
                        elif f_eqn1_in==factor_eqn1:
                            st.write('Good! Now solve it:') # correct solution is 
                            ans = list({b//a, -1*b//a, b//gcf, -1*b//gcf, a//gcf, -1*a//gcf, gcf, -1*gcf, a, -1*a, b, -1*b})
                            ans.sort()
                            soln1_in = st.selectbox('Solution to '+factor_eqn1+ ':',['SELECT'] + ans)
                            if (soln1_in!=(-1*b//a)):
                                st.write('Try again.')
                            elif soln1_in==-1*b//a: # {a}/{gcf} x + {b}/{gcf} = 0 --> {a}/{gcf} x = -{b}/{gcf} -->  x = -({b}/{gcf})/({a}/{gcf}) = -{b}/{a}
                                st.write('Great job! You solved it!')
                                st.balloons()

            else: # a, b, and c all non-zero; trinomial factoring

                common = [f for f in factorlist if (a%f==0) and (b%f==0) and (c%f==0)] # look for a gcf
                if len(common)>0:
                    if a<0:
                        gcf = min(common)
                    else:
                        gcf = max(common)
                else:
                    gcf = 1

                gcf_in = st.selectbox('What is the GCF (if there is no GCF besides 1, select "1")',['SELECT'] + coef_options)
                if (gcf_in!=gcf):
                    st.write('Not quite. Try again.')
                elif gcf_in==gcf:
                    st.write('Great job!')
                    if gcf==1:
                        a1 = a
                        disp_a1 = disp_a
                        b1 = b
                        c1 = c
                        equation1 = equation0
                    else:
                        st.write(f'So we can factor out {gcf}, and the new equation is:')
                        a1 = a//gcf
                        b1 = b//gcf
                        c1 = c//gcf
                        if a1 == 1:
                            disp_a1 = 'x^2'
                        else:
                            disp_a1 = f'{a1}x^2'
                        equation1 = f'{gcf}(' + disp_a1 + f' + {b1}x + {c1}) = 0'
                        st.latex(equation1)

                    # factoring method (after gcf) -- look for pair of numbers that multiply to a*c and add to b. Then use area model to factor to binomials
                    st.write(f'a*c = {a1*c1}, and b = {b1}. Can you find a pair of numbers that multiply to give {a1*c1} and add to give {b1}?')
                    st.write('If so, select them here. If there is no such pair, try another solving method.')
                    num1 = st.selectbox('1st number',['SELECT'] + coef_options)
                    num2 = st.selectbox('2nd number',['SELECT'] + coef_options)
                    if (num1!='SELECT') and (num2!='SELECT'):
                        if (np.abs(num1+num2-b1)>0.0001) or (np.abs((num1*num2)-(a1*c1))>0.0001): # not a match (to within roundoff error)
                            st.write('Not quite. Keep trying or try another method.')
                        elif (np.abs(num1+num2-b1)<=0.0001) and (np.abs((num1*num2)-(a1*c1))<=0.0001): # they found the right pair
                            st.write("You're going great! Scroll down to view the area model and fill in the row and column greatest common factors:")
                            # the rows and columns refer to the area model, below
                            gcfR1 = st.selectbox('How many "x" can you factor out of the first row?',['SELECT'] + coef_options)
                            gcfR2 = st.selectbox('What is the greatest common factor of the second row?',['SELECT'] + coef_options)
                            gcfC1 = st.selectbox('How many "x" can you factor out of the first column?',['SELECT'] + coef_options)
                            gcfC2 = st.selectbox('What is the greatest common factor of the second column?',['SELECT'] + coef_options)

                            # display the area model
                            if gcfR1 == 1:
                                dispR1 = 'x'
                            else:
                                dispR1 = f'{gcfR1}x'
                            if gcfC1 == 1:
                                dispC1 = 'x'
                            else:
                                dispC1 = f'{gcfC1}x'

                            box_df = pd.DataFrame({
                                '0': ['', '', dispR1, gcfR2],
                                ' ': ['', '', '|', '|'],
                                '  ': [dispC1, '____________', disp_a1, f'{num2}x'],
                                '   ': [gcfC2, '____________', f'{num1}x', f'{c}']
                            })
                            box_df.set_index('0',inplace=True)
                            st.table(box_df)
                            if (gcfR1=='SELECT') or (gcfR2=='SELECT') or (gcfC1=='SELECT') or (gcfC2=='SELECT'):
                                st.write()
                            elif (gcfR1*gcfC1!=a1) or (gcfR1*gcfC2!=num1) or (gcfR2*gcfC1!=num2) or (gcfR2*gcfC2!=c1):
                                st.write('Not quite; keep trying!')
                            # otherwise, they have correctly factored using the area model:
                            elif (gcfR1==gcfC1) and (gcfR2==-1*gcfC2):   # ax^2 - b, where a and b are perfect squares
                                st.write('This looks like a special case, called "difference of squares". Select all correct solutions:')
                                solution_options = list({gcfR2/gcfR1, -1*gcfR2/gcfR1, gcfR1/gcfR2, -1*gcfR1/gcfR2})
                                solution_options.sort()
                                solution_options = [str(np.round(s,4)) for s in solution_options]
                                correct = [-1*gcfR2/gcfR1, gcfR2/gcfR1]
                                correct = [str(np.round(s,4)) for s in correct]
                                sel1 = st.checkbox(solution_options[0])
                                sel2 = st.checkbox(solution_options[1])
                                sel3 = st.checkbox(solution_options[2])
                                sel4 = st.checkbox(solution_options[3])

                                if   (sel1==True) and (solution_options[0] not in correct): st.write('Try again.')
                                elif (sel2==True) and (solution_options[1] not in correct): st.write('Try again.')
                                elif (sel3==True) and (solution_options[2] not in correct): st.write('Try again.')
                                elif (sel4==True) and (solution_options[3] not in correct): st.write('Try again.')
                                elif (sel1!=True) and (solution_options[0] in correct): st.write('Try again.')
                                elif (sel2!=True) and (solution_options[1] in correct): st.write('Try again.')
                                elif (sel3!=True) and (solution_options[2] in correct): st.write('Try again.')
                                elif (sel4!=True) and (solution_options[3] in correct): st.write('Try again.')
                                else:
                                    st.write('You did it!')
                                    st.balloons()

                            elif (gcfR1*gcfC1==a1) and (gcfR1*gcfC2==num1) and (gcfR2*gcfC1==num2) and (gcfR2*gcfC2==c1): # correctly factored
                                st.write('Good job! Almost there; we have our factors now.')
                                if gcfR2<0:
                                    dispR2 = f' - {-1*gcfR2}'
                                else:
                                    dispR2 = f' + {gcfR2}'
                                if gcfC2<0:
                                    dispC2 = f' - {-1*gcfC2}'
                                else:
                                    dispC2 = f' + {gcfC2}'
                                if gcf==1: # write out the new factored equation
                                    equation2 = '(' + dispR1 + dispR2 + ')(' + dispC1 + dispC2 + ') = 0'
                                else:
                                    equation2 = f'{gcf}(' + dispR1 + dispR2 + ')(' + dispC1 + dispC2 + ') = 0'
                                st.write(equation2)
                                st.write('Scroll down to select and solve the 2 linear equations:')

                                factor_eqn1 = dispR1 + dispR2 + ' = 0'
                                factor_eqn2 = dispC1 + dispC2 + ' = 0'
                                f_eqn1_in = st.selectbox('Which of these equations should you solve?',['SELECT', factor_eqn1.replace('-','+'), factor_eqn1.replace('+','-')])
                                f_eqn2_in = st.selectbox('Which of these equations should you solve?',['SELECT', factor_eqn2.replace('-','+'), factor_eqn2.replace('+','-')])
                                if (f_eqn1_in=='SELECT') or (f_eqn2_in=='SELECT'):
                                    st.write()
                                elif (f_eqn1_in!=factor_eqn1) or (f_eqn2_in!=factor_eqn2):
                                    st.write('Try again. Hint: The factors should be set equal to zero because anything multiplied by zero is zero.')
                                elif (f_eqn1_in==factor_eqn1) and (f_eqn2_in==factor_eqn2):
                                    st.write('Good! Now solve them:')
                                    ans = list({gcfR1*gcfR2, gcfR2, gcfR2/gcfR1, gcfR1, -1*gcfR1*gcfR2, -1*gcfR2, -1*gcfR2/gcfR1, -1*gcfR1, gcfC1*gcfC2, gcfC2, gcfC2/gcfC1, gcfC1, -1*gcfC1*gcfC2, -1*gcfC2, -1*gcfC2/gcfC1, -1*gcfC1})
                                    ans.sort()
                                    soln1_in = st.selectbox('Solution to '+factor_eqn1+ ':',['SELECT'] + ans)
                                    soln2_in = st.selectbox('Solution to '+factor_eqn2+ ':',['SELECT'] + ans)
                                    if (soln1_in=='SELECT') or (soln2_in=='SELECT'):
                                        st.write()
                                    elif (soln1_in!=(-1*gcfR2/gcfR1)) or (soln2_in!=(-1*gcfC2/gcfC1)):
                                        st.write('Try again.')
                                    elif (soln1_in==(-1*gcfR2/gcfR1)) and (soln2_in==(-1*gcfC2/gcfC1)):
                                        st.write('Great job! You solved it!')
                                        st.balloons()
                                        
        ############################################### SOLVE BY COMPLETING THE SQUARE ###############################################

        if slv_mthd == 'Completing the square':
            
            st.write('Step 1: Move the constant to the other side.')
            rhs_choices = [c, -1*c]
            rhs_choices.sort()
            rhs = st.selectbox('What number goes on the right?',['SELECT'] + rhs_choices)
            
            equation1 = disp_a + f' + {b}x = {rhs}' # ax^2+ bx = -c
            
            
            if rhs=='SELECT':
                st.write()
            elif rhs!=(-1*c):
                st.write('What happens to the sign of a number when you add or subtract to move it to the other side?')
            elif rhs==(-1*c):
                st.latex(equation1)
                step1 = False
                if a!=1:
                    st.write('Since a is not 1, we need to factor it out of the left hand side.')
                    b1 = b/a
                    equation2 = f'{a}(x^2 + {b1}x) = {rhs}' # a(x^2 + [b1]x) = -c where b1 = b/a
                    
                    b1_choices = list({b, -1*b, b1, -1*b1, a})
                    b1_choices.sort()
                    msg_a = f'When you factor out {a}, what is the new coefficient of x?'
                    b1_in = st.selectbox(msg_a,['SELECT'] + b1_choices)
                    if b1_in == 'SELECT':
                        st.write()
                    elif b1_in!=(b/a):
                        st.write('Try again.')
                    elif b1_in==(b/a):
                        st.write('Nicely done!')
                        st.latex(equation2)
                        step1 = True
                else:
                    equation2 = equation1
                    b1 = b
                    step1 = True
                if step1:
                    st.write('Step 2: We need to "complete the square" by adding the value of $(b/2)^2$ to the quadratic on the left.')
                    bover2 = b1/2
                    bover2sq = b1*b1/4
                    abover2sq = a*bover2sq
                    if a!=1:
                        equation3 = f'{a}(x^2 + {b1}x + {bover2sq}) = {rhs+abover2sq}' # a(x^2 + [b1]x + [b1/2]^2) = -c + a[b1/2]^2
                    else:
                        equation3 = f'(x^2 + {b1}x + {bover2sq}) = {rhs+abover2sq}'

                    add_opt = list({b1, -1*b1, bover2, -1*bover2, bover2sq, rhs/2, rhs*rhs/4, a*bover2, abover2sq})
                    add_opt.sort()
                    add_inL = st.selectbox('What should you add on the left?',['SELECT'] + add_opt)
                    if a!=1:
                        st.write(f"Be careful on the right hand side, don't forget we have that factor of {a}!")
                    add_inR = st.selectbox('What should you add on the right?',['SELECT'] + add_opt)
                    if (add_inL=='SELECT') or (add_inR=='SELECT'):
                        st.write()
                    elif (add_inL!=bover2sq) or (add_inR!=abover2sq):
                        st.write('Try again.')
                    elif (add_inL==bover2sq) and (add_inR==abover2sq):
                        st.write('Great!')
                        st.latex(equation3)
                        st.write('We now have a "perfect square trinomial" on the left.')
                        st.write('This can be rewritten as $(x + [ ])^2$, where the number in the blank is $b/2$.')
                        rhs1 = rhs + abover2sq
                        if a!=1:
                            equation4 = f'{a}(x + {bover2})^2 = {rhs1}'
                        else:
                            equation4 = f'(x + {bover2})^2 = {rhs1}'


                        binom_in = st.selectbox('What should go in the blank?',['SELECT'] + add_opt)
                        if binom_in=='SELECT':
                            st.write()
                        if binom_in!=bover2:
                            st.write('Try again.')
                        elif binom_in==bover2:
                            st.write('Nice.')
                            st.latex(equation4)
                            step2 = False
                            if a!=1:
                                rhs2 = rhs1/a
                                equation5 = f'(x + {bover2})^2 = {rhs2}'    # (x + [b1/2])^2 = [-c + a[b1/2]^2]/a

                                st.write('This is a good time to divide by "a".')
                                rhs_opt = list({rhs1, rhs2, rhs1*a, rhs2/2, b/a, b/(2*a)})
                                rhs_opt.sort()
                                new_rhs_in = st.selectbox('What would be on the right hand side after dividing by "a"?',['SELECT'] + rhs_opt)

                                if new_rhs_in=='SELECT':
                                    st.write()
                                elif new_rhs_in!=rhs2:
                                    st.write('Try again.')
                                elif new_rhs_in==rhs2: 
                                    st.write('Good job!')
                                    st.latex(equation5)
                                    step2 = True
                            else:
                                rhs2 = rhs1
                                equation5 = equation4
                                step2 = True
                            if step2:
                                st.write("Step 3: Now it's time to take the square root of both sides.")
                                
                                # if the number under the square root is positive, there are two real solutions.  If it is 0, there is one real solution.
                                # if it is negative, then there are no real solutions, 
                                # but students who have learned complex numbers can continue to fine the two complex solutions
                                soln_opt = ['2 REAL solutions', '1 REAL solution', 'No REAL solutions (2 COMPLEX solutions)']
                                if rhs2<0: soln = soln_opt[2]
                                elif rhs2==0: soln = soln_opt[1]
                                else: soln = soln_opt[0]
                                num_sol = st.selectbox('Look at the right hand side -- how many and what type of solutions will this give?', ['SELECT'] + soln_opt)
                                if num_sol=='SELECT':
                                    st.write()
                                elif num_sol!=soln:
                                    st.write('Try again.')
                                elif num_sol==soln:
                                    if rhs2<0: # no real solutions, 2 complex solutions
                                        st.write('Uh oh! The right hand side is negative.')
                                        st.write('There are no REAL numbers that can square to give a negative number.')
                                        st.write("If you're in algebra 1 right now, you can stop here - the answer is 'no real solutions'.")
                                        st.write("But if you're in algebra 2 or another advanced math class, it's a little trickier.")
                                        cont = st.selectbox('Continue on to find the 2 complex solutions?',['SELECT', 'yes', 'no'])
                                        if cont == 'no':
                                            st.write('OK, good job on this problem!') # okay to stop here for algebra 1 students
                                        elif cont== 'yes': # for those prepared to continue
                                            st.write('We know that the square root of -1 is "i". So we can take that out of the square root, and drop the negative.')
                                            equation6 = f'$x + {bover2} = \pm \sqrt({rhs2})$'
                                            equation7 = f'$x + {bover2} = \pm i \sqrt({-1*rhs2})$'
                                            equation7a= f'$x + {bover2} = i \sqrt({-1*rhs2})$'
                                            equation7b= f'$x + {bover2} = -i \sqrt({-1*rhs2})$'
                                            st.write('So instead of : ' + equation6 + ', we can write : ' + equation7)
                                            st.write("and that's actually two equations, " + equation7a + ' and ' + equation7b + '.')

                                            out_rad, in_rad, denom = simplify_radical(-1*rhs2) # simplify the radical


                                            if (out_rad!=None) and (in_rad!=-1*rhs2): # note al of these will include "i"!

                                                if in_rad!=1: # format the equations depending on whether there is still a square root, a number outside, and/or a denominator
                                                    if out_rad!=1:
                                                        if denom!=1:
                                                            equation8a= f'$x + {bover2} = {out_rad}i \sqrt({in_rad})/{denom}$'
                                                            equation8b= f'$x + {bover2} = -{out_rad}i \sqrt({in_rad})/{denom}$'
                                                        else:
                                                            equation8a= f'$x + {bover2} = {out_rad}i \sqrt({in_rad})$'
                                                            equation8b= f'$x + {bover2} = -{out_rad}i \sqrt({in_rad})$'
                                                    else:
                                                        if denom!=1:
                                                            equation8a= f'$x + {bover2} = i \sqrt({in_rad})/{denom}$'
                                                            equation8b= f'$x + {bover2} = -i \sqrt({in_rad})/{denom}$'
                                                        else:
                                                            equation8a= f'$x + {bover2} = i \sqrt({in_rad})$' 
                                                            equation8b= f'$x + {bover2} = -i \sqrt({in_rad})$'
                                                else:
                                                    if out_rad!=1:
                                                        if denom!=1:
                                                            equation8a= f'$x + {bover2} = {out_rad}i /{denom}$'
                                                            equation8b= f'$x + {bover2} = -{out_rad}i /{denom}$'
                                                        else:
                                                            equation8a= f'$x + {bover2} = {out_rad}i$'
                                                            equation8b= f'$x + {bover2} = -{out_rad}i$'
                                                    else:
                                                        if denom!=1:
                                                            equation8a= f'$x + {bover2} = i /{denom}$'
                                                            equation8b= f'$x + {bover2} = -i /{denom}$'
                                                        else:
                                                            equation8a= f'$x + {bover2} = i $'
                                                            equation8b= f'$x + {bover2} = -i $'



                                                st.write('Can you simplify the radical? You will probably need some scratch paper!')
                                                out_str = f'$i \sqrt({-1*rhs2}) = [ ] i \sqrt( [ ] )/ [ ]$'
                                                st.write(out_str)
                                                choices = list(range(1,201))
                                                out1 = st.selectbox('First blank = ',['SELECT'] + choices)
                                                in1  = st.selectbox('Second blank = ',['SELECT'] + choices)
                                                den1 = st.selectbox('Last blank = ',['SELECT'] + choices) 
                                                if (out1=='SELECT') or (in1=='SELECT') or (den1=='SELECT'):
                                                    st.write()
                                                elif (out1!=out_rad) or (in1!=in_rad) or (den1!=denom):
                                                    st.write('Try again.')
                                                elif (out1==out_rad) and (in1==in_rad) and (den1==denom):
                                                    st.write('Great! So now we have: ' + equation8a + ' and ' + equation8b + '.')
                                            else:
                                                in_rad = -1*rhs2
                                                out_rad = 1
                                                denom = 1
                                                equation8a = equation7a
                                                equation8b = equation7b

                                            st.write('Step 4: Last step! Get x by itself on the left side of both equations.')
                                            st.write('Select all correct solutions:')

                                            # format answers (correct and incorrect) according to whether there is a square root, a number outside, and/or a fraction
                                            if in_rad!=1: 
                                                if (out_rad!=1) and (denom!=1):
                                                    soln1 = f'{-1*bover2} + {out_rad}i square_root({in_rad})/{denom}'
                                                    soln2 = f'{-1*bover2} - {out_rad}i square_root({in_rad})/{denom}'
                                                    wrong1= f'{bover2} + {out_rad}i square_root({in_rad})/{denom}'
                                                    wrong2= f'{bover2} - {out_rad}i square_root({in_rad})/{denom}'
                                                elif out_rad!=1:
                                                    soln1 = f'{-1*bover2} + {out_rad}i square_root({in_rad})'
                                                    soln2 = f'{-1*bover2} - {out_rad}i square_root({in_rad})'
                                                    wrong1= f'{bover2} + {out_rad}i square_root({in_rad})'
                                                    wrong2= f'{bover2} - {out_rad}i square_root({in_rad})'
                                                elif denom!=1:
                                                    soln1 = f'{-1*bover2} + i square_root({in_rad})/{denom}'
                                                    soln2 = f'{-1*bover2} - i square_root({in_rad})/{denom}'
                                                    wrong1= f'{bover2} + i square_root({in_rad})/{denom}'
                                                    wrong2= f'{bover2} - i square_root({in_rad})/{denom}'
                                                else:
                                                    soln1 = f'{-1*bover2} + i square_root({in_rad})'
                                                    soln2 = f'{-1*bover2} - i square_root({in_rad})'
                                                    wrong1= f'{bover2} + i square_root({in_rad})'
                                                    wrong2= f'{bover2} - i square_root({in_rad})'
                                            else:
                                                if (out_rad!=1) and (denom!=1):
                                                    soln1 = f'{-1*bover2} + {out_rad}i/{denom}'
                                                    soln2 = f'{-1*bover2} - {out_rad}i/{denom}'
                                                    wrong1= f'{bover2} + {out_rad}i/{denom}'
                                                    wrong2= f'{bover2} - {out_rad}i/{denom}'
                                                elif out_rad!=1:
                                                    soln1 = f'{-1*bover2} + {out_rad}i'
                                                    soln2 = f'{-1*bover2} - {out_rad}i'
                                                    wrong1= f'{bover2} + {out_rad}i'
                                                    wrong2= f'{bover2} - {out_rad}i'
                                                elif denom!=1:
                                                    soln1 = f'{-1*bover2} + i/{denom}'
                                                    soln2 = f'{-1*bover2} - i/{denom}'
                                                    wrong1= f'{bover2} + i/{denom}'
                                                    wrong2= f'{bover2} - i/{denom}'
                                                else:
                                                    soln1 = f'{-1*bover2} + i'
                                                    soln2 = f'{-1*bover2} - i'
                                                    wrong1= f'{bover2} + i'
                                                    wrong2= f'{bover2} - i'

                                            solution_options = list({soln1, soln2, wrong1, wrong2})
                                            solution_options.sort()
                                            correct = [soln1, soln2]

                                            if b!=0:
                                                sel1 = st.checkbox(solution_options[0])
                                                sel2 = st.checkbox(solution_options[1])
                                                sel3 = st.checkbox(solution_options[2])
                                                sel4 = st.checkbox(solution_options[3])

                                                if   (sel1==True) and (solution_options[0] not in correct): st.write('Try again.')
                                                elif (sel2==True) and (solution_options[1] not in correct): st.write('Try again.')
                                                elif (sel3==True) and (solution_options[2] not in correct): st.write('Try again.')
                                                elif (sel4==True) and (solution_options[3] not in correct): st.write('Try again.')
                                                elif (sel1!=True) and (solution_options[0] in correct): st.write('Try again.')
                                                elif (sel2!=True) and (solution_options[1] in correct): st.write('Try again.')
                                                elif (sel3!=True) and (solution_options[2] in correct): st.write('Try again.')
                                                elif (sel4!=True) and (solution_options[3] in correct): st.write('Try again.')
                                                else:
                                                    st.write('You did it!')
                                                    st.balloons()
                                            else: # if b = 1, it's a simpler choice -- only 2 choices, and they should BOTH be selected
                                                sel1 = st.checkbox(correct[0])
                                                sel2 = st.checkbox(correct[1])

                                                if (sel1!=True):   st.write('Try again.')
                                                elif (sel2!=True): st.write('Try again.')
                                                else:
                                                    st.write('You did it!')
                                                    st.balloons()

                                    elif rhs2==0: # case where the right hand side is zero. +/- SQRT(0) = 0, so there i just one solution
                                        st.write('Interesting -  The right hand side is zero.')
                                        st.write('The square root of zero is still zero, and negative zero is still zero.')
                                        st.write("So, there's only one equation (the 'plus or minus' part is gone), and only one solution!")

                                        equation6 = f'x + {bover2} = 0'
                                        st.write(equation6)

                                        st.write('Step 4: Last step! Get x by itself on the left side of both equations.')
                                        st.write('Select the correct solution:')

                                        soln1 = f'{-1*bover2}'
                                        wrong1= f'{bover2}'
                                        solution_options = [soln1, wrong1]

                                        solution_options.sort()
                                        sel0 = st.checkbox('impossible to solve')
                                        sel1 = st.checkbox(solution_options[0])
                                        sel2 = st.checkbox(solution_options[1])
                                        if sel0==True: st.write('Try again.')
                                        elif (sel1==True) and (solution_options[0] != soln1): st.write('Try again.')
                                        elif (sel2==True) and (solution_options[1] != soln1): st.write('Try again.')
                                        elif (sel1!=True) and (solution_options[0] == soln1): st.write('Try again.')
                                        elif (sel2!=True) and (solution_options[1] == soln1): st.write('Try again.')
                                        else:
                                            st.write('You did it!')
                                            st.balloons()
                                    else: # case with two real solutions (no complex numbers needed)
                                        st.write('Correct, the right hand side is positive.')
                                        st.write("There is no problem taking the square root of a positive number, so we will have 2 REAL solutions because of the 'plus or minus'.")
                                        equation6 = f'$x + {bover2} = \pm \sqrt({rhs2})$' # x + b1/2 = +/- sqrt(right hand side)
                                        equation6a= f'$x + {bover2} =  \sqrt({rhs2})$'    # x + b1/2 =     sqrt(right hand side)
                                        equation6b= f'$x + {bover2} = - \sqrt({rhs2})$'   # x + b1/2 =   - sqrt(right hand side)
                                        st.write(equation6 + ' is actually two equations:')
                                        st.write(equation6a + ' and ' + equation6b + '.')

                                        out_rad, in_rad, denom = simplify_radical(rhs2) # simplify the radical


                                        if (out_rad!=None) and (in_rad!=rhs2): #format according to whether there is still a radical, and/or a fraction, etc.
                                            if in_rad!=1:
                                                if out_rad!=1:
                                                    if denom!=1:
                                                        equation8a= f'$x + {bover2} = {out_rad} \sqrt({in_rad})/{denom}$'  # x + b1/2 = [] sqrt([])/[] 
                                                        equation8b= f'$x + {bover2} = -{out_rad} \sqrt({in_rad})/{denom}$' # x + b1/2 =-[] sqrt([])/[]
                                                    else:
                                                        equation8a= f'$x + {bover2} = {out_rad} \sqrt({in_rad})$'  # x + b1/2 = [] sqrt([])
                                                        equation8b= f'$x + {bover2} = -{out_rad} \sqrt({in_rad})$' # x + b1/2 =-[] sqrt([])

                                                else:
                                                    if denom!=1:
                                                        equation8a= f'$x + {bover2} = \sqrt({in_rad})/{denom}$'  # x + b1/2 = sqrt([])/[]
                                                        equation8b= f'$x + {bover2} = -\sqrt({in_rad})/{denom}$' # x + b1/2 =-sqrt([])/[]
                                                    else:
                                                        equation8a= f'$x + {bover2} = \sqrt({in_rad})$'  # x + b1/2 = sqrt([])
                                                        equation8b= f'$x + {bover2} = -\sqrt({in_rad})$' # x + b1/2 =-sqrt([])

                                            else:
                                                if out_rad!=1:
                                                    if denom!=1:
                                                        equation8a= f'$x + {bover2} = {out_rad}/{denom}$'  # x + b1/2 = []/[]
                                                        equation8b= f'$x + {bover2} = -{out_rad}/{denom}$' # x + b1/2 =-[]/[]
                                                    else:
                                                        equation8a= f'$x + {bover2} = {out_rad}$'  # x + b1/2 = []
                                                        equation8b= f'$x + {bover2} = -{out_rad}$' # x + b1/2 =-[]
                                                else:
                                                    if denom!=1:
                                                        equation8a= f'$x + {bover2} = 1/{denom}$'  # x + b1/2 = 1/[]
                                                        equation8b= f'$x + {bover2} = -1/{denom}$' # x + b1/2 =-1/[]
                                                    else:
                                                        equation8a= f'$x + {bover2} = 1$'  # x + b1/2 = 1
                                                        equation8b= f'$x + {bover2} = -1$' # x + b1/2 =-1


                                            st.write('Can you simplify the radical? You will probably need some scratch paper!')
                                            out_str = f'\sqrt({rhs2}) = [ ] \sqrt( [ ] )/ [ ]'
                                            st.latex(out_str)
                                            choices = list(range(1,201))
                                            out1 = st.selectbox('First blank = ',['SELECT'] + choices)
                                            in1  = st.selectbox('Second blank = ',['SELECT'] + choices)
                                            den1 = st.selectbox('Last blank = ',['SELECT'] + choices)
                                            if (out1=='SELECT') or (in1=='SELECT') or (den1=='SELECT'):
                                                st.write()
                                            if (out1!=out_rad) or (in1!=in_rad) or (den1!=denom):
                                                st.write('Try again.')
                                            else:
                                                st.write('Great! So now we have: ' + equation8a + ' and ' + equation8b + '.')
                                        else:
                                            in_rad = rhs2
                                            out_rad = 1
                                            denom = 1
                                            equation8a = equation6a
                                            equation8b = equation6b

                                        st.write('Step 4: Last step! Get x by itself on the left side of both equations.')
                                        st.write('Select all correct solutions:')
                                        if in_rad!=1:
                                            if (out_rad!=1) and (denom!=1):
                                                soln1 = f'{-1*bover2} + {out_rad} square_root({in_rad})/{denom}' # x = -b1/2 + [] sqrt([])/[]
                                                soln2 = f'{-1*bover2} - {out_rad} square_root({in_rad})/{denom}' # x = -b1/2 - [] sqrt([])/[]
                                                wrong1= f'{bover2} + {out_rad} square_root({in_rad})/{denom}' # x = b1/2 + [] sqrt([])/[]
                                                wrong2= f'{bover2} - {out_rad} square_root({in_rad})/{denom}' # x = b1/2 - [] sqrt([])/[]
                                            elif out_rad!=1:
                                                soln1 = f'{-1*bover2} + {out_rad} square_root({in_rad})' # x = -b1/2 + [] sqrt([])
                                                soln2 = f'{-1*bover2} - {out_rad} square_root({in_rad})' # x = -b1/2 - [] sqrt([])
                                                wrong1= f'{bover2} + {out_rad} square_root({in_rad})' # x = b1/2 + [] sqrt([])
                                                wrong2= f'{bover2} - {out_rad} square_root({in_rad})' # x = b1/2 - [] sqrt([])
                                            elif denom!=1:
                                                soln1 = f'{-1*bover2} + square_root({in_rad})/{denom}' # x = -b1/2 + sqrt([])/[]
                                                soln2 = f'{-1*bover2} - square_root({in_rad})/{denom}' # x = -b1/2 - sqrt([])/[]
                                                wrong1= f'{bover2} + square_root({in_rad})/{denom}' # x = b1/2 + sqrt([])/[]
                                                wrong2= f'{bover2} - square_root({in_rad})/{denom}' # x = b1/2 - sqrt([])/[]
                                            else:
                                                soln1 = f'{-1*bover2} + square_root({in_rad})' # x = -b1/2 + sqrt([])
                                                soln2 = f'{-1*bover2} - square_root({in_rad})' # x = -b1/2 - sqrt([])
                                                wrong1= f'{bover2} + square_root({in_rad})' # x = b1/2 + sqrt([])
                                                wrong2= f'{bover2} - square_root({in_rad})' # x = b1/2 - sqrt([])
                                        else:
                                            if (out_rad!=1) and (denom!=1):
                                                soln1 = combine_string(f'{-1*bover2} + {out_rad}/{denom}') # x = -b1/2 + []/[]                                        
                                                soln2 = combine_string(f'{-1*bover2} - {out_rad}/{denom}') # x = -b1/2 - []/[]
                                                wrong1= combine_string(f'{bover2} + {out_rad}/{denom}') # x = b1/2 + []/[]
                                                wrong2= combine_string(f'{bover2} - {out_rad}/{denom}') # x = b1/2 - []/[]
                                            elif out_rad!=1:
                                                soln1 = combine_string(f'{-1*bover2} + {out_rad}') # x = -b1/2 + []
                                                soln2 = combine_string(f'{-1*bover2} - {out_rad}') # x = -b1/2 - []
                                                wrong1= combine_string(f'{bover2} + {out_rad}') # x = b1/2 + []
                                                wrong2= combine_string(f'{bover2} - {out_rad}') # x = b1/2 - []
                                            elif denom!=1:
                                                soln1 = combine_string(f'{-1*bover2} + 1/{denom}') # x = -b1/2 + 1/[]
                                                soln2 = combine_string(f'{-1*bover2} - 1/{denom}') # x = -b1/2 - 1/[]
                                                wrong1= combine_string(f'{bover2} + 1/{denom}') # x = b1/2 + 1/[]
                                                wrong2= combine_string(f'{bover2} - 1/{denom}') # x = b1/2 - 1/[]
                                            else:
                                                soln1 = combine_string(f'{-1*bover2} + 1') # x = -b1/2 + 1
                                                soln2 = combine_string(f'{-1*bover2} - 1') # x = -b1/2 - 1
                                                wrong1= combine_string(f'{bover2} + 1') # x = b1/2 + 1
                                                wrong2= combine_string(f'{bover2} - 1') # x = b1/2 - 1

                                        solution_options = list({soln1, soln2, wrong1, wrong2})
                                        correct = [soln1, soln2]

                                        solution_options.sort()
                                        if b!=0:
                                            
                                            sel1 = st.checkbox(solution_options[0])
                                            sel2 = st.checkbox(solution_options[1])
                                            sel3 = st.checkbox(solution_options[2])
                                            sel4 = st.checkbox(solution_options[3])
                                            if   (sel1==True) and (solution_options[0] not in correct): st.write('Try again.')
                                            elif (sel2==True) and (solution_options[1] not in correct): st.write('Try again.')
                                            elif (sel3==True) and (solution_options[2] not in correct): st.write('Try again.')
                                            elif (sel4==True) and (solution_options[3] not in correct): st.write('Try again.')
                                            elif (sel1!=True) and (solution_options[0] in correct): st.write('Try again.')
                                            elif (sel2!=True) and (solution_options[1] in correct): st.write('Try again.')
                                            elif (sel3!=True) and (solution_options[2] in correct): st.write('Try again.')
                                            elif (sel4!=True) and (solution_options[3] in correct): st.write('Try again.')
                                            else:
                                                st.write('You did it!')
                                                st.balloons()
                                        else: # b = 0, only 2 answer choices, both are correct
                                            correct = [c.replace('-0.0 ','') for c in correct]
                                            correct = [c.replace('0.0 ','') for c in correct]
                                            sel1 = st.checkbox(correct[0])
                                            sel2 = st.checkbox(correct[1])
                                            if (sel1!=True):   st.write('Try again.')
                                            elif (sel2!=True): st.write('Try again.')
                                            else:
                                                st.write('You did it!')
                                                st.balloons()
        
        ############################################### SOLVE BY THE QUADRATIC FORMULA ###############################################
                                     
        if slv_mthd == 'Quadratic Formula':

            st.write('The nice thing about the quadratic formula is, it will ALWAYS work.')
            st.write('The less nice thing is the computations can get messy.')
            quad_formula = 'x = [ -b \pm \sqrt( b^2 - 4ac )] / (2a)'
            st.latex(quad_formula)
            st.write('That bit inside the square root is called the DISCRIMINANT: $d = b^2 - 4ac$.')
            st.write('Scroll down to calculate the discriminant.')
            
            disc_df = pd.DataFrame({
                '0': ['d > 0', 'd = 0', 'd < 0'],
                ' ': ['2 REAL solutions', 'Exactly 1 REAL solution', '0 REAL solutions, 2 COMPLEX solutions']
            })
            disc_df.set_index('0',inplace=True)
            st.table(disc_df)

            disc = b*b - 4*a*c
            disc_in_str = st.text_input('d = b^2 - 4ac = ', value='')
            if disc_in_str!='':
                disc_in = int(disc_in_str)

                soln_opts = ['2 REAL solutions', 'Exactly 1 REAL solution', '0 REAL solutions, 2 COMPLEX solutions']
                n_solns_in = st.selectbox('How many solutions should there be?',['SELECT'] + soln_opts)
                if disc < 0: n_solns = soln_opts[2]
                elif disc==0: n_solns = soln_opts[1]
                else: n_solns = soln_opts[0]

                if n_solns_in=='SELECT':
                    st.write()
                elif (disc_in!=disc) or (n_solns_in!=n_solns):
                    st.write('Not quite. Try again.')
                else:
                    st.write(f'Great, so we now have: $x = [ [ ] \pm \sqrt( {disc} )] / [ ]$')

                    negb = -1*b
                    twoa = 2*a
                    options = list({a, -1*a, twoa, -2*a, b, negb, 2*b, -2*b, c, -1*c, 2*c, -2*c})
                    options.sort()
                    negb_in = st.selectbox('what goes in the first blank?',['SELECT'] + options)
                    twoa_in = st.selectbox('What goes in the second blank, the one in the denominator?',['SELECT'] + options)
                    if (negb_in=='SELECT') or (twoa_in=='SELECT'):
                        st.write()
                    elif (negb_in!=negb) or (twoa_in!=twoa):
                        st.write('Try again.')
                    else:
                        st.write(f'Good! So now we have: $x = [ {negb} \pm \sqrt( {disc} )] / {twoa}$')
                        st.write(f'Or, two equations: $x = [ {negb} + \sqrt( {disc} )] / {twoa}$ and $x = [ {negb} - \sqrt( {disc} )] / {twoa}$')
                    if disc < 0:
                        st.write('Uh oh! The discriminant is negative.')
                        st.write('There are no REAL numbers that can square to give a negative number.')
                        st.write("If you're in algebra 1 right now, you can stop here - the answer is 'no real solutions'.")
                        st.write("But if you're in algebra 2 or another advanced math class, it's a little trickier.")
                        cont = st.selectbox('Continue on to find the 2 complex solutions?',['SELECT', 'yes', 'no'])
                        if cont == 'SELECT':
                            st.write()
                        elif cont == 'no':
                            st.write('OK, good job on this problem!')
                        else:

                            st.write('We know that the square root of -1 is "i". So we can take that out of the square root, and drop the negative.')
                            st.write(f'$x = [ {negb} + i \sqrt( {-1*disc} )] / {twoa}$ and $x = [ {negb} - i \sqrt( {-1*disc} )] / {twoa}$')

                            out_rad, in_rad, denom = simplify_radical(-1*disc)


                            if (out_rad!=None) and (in_rad!=-1*disc):

                                st.write('Can you simplify the radical? You will probably need some scratch paper!')
                                out_str = f'i \sqrt({-1*disc}) = [ ] i \sqrt( [ ] )/ [ ] '
                                st.latex(out_str)
                                choices = list(range(1,21))
                                if np.abs(disc)>20: choices.append(np.abs(disc))
                                out1 = st.selectbox('First blank = ',['SELECT'] + choices)
                                in1  = st.selectbox('Second blank = ',['SELECT'] + choices)
                                den1 = st.selectbox('Last blank = ',['SELECT'] + choices)
                                if (out1=='SELECT') or (in1=='SELECT') or (den1=='SELECT'):
                                    st.write()
                                elif (out1!=out_rad) or (in1!=in_rad) or (den1!=denom):
                                    st.write('Try again.')
                                else:
                                    st.write(f'Good! So now (separating the two parts of the fraction) we have: $x = {negb}/{twoa} \pm {out_rad}i \sqrt( {in_rad} ) / [ ]$')
                                    denom_new = denom*twoa

                                    if in_rad!=1:
                                        if out_rad!=1:
                                            if denom!=1:
                                                equation8a = f'$x = {negb}/{twoa} + {out_rad}i \sqrt( {in_rad} ) / {denom_new}$'
                                                equation8b = f'$x = {negb}/{twoa} - {out_rad}i \sqrt( {in_rad} ) / {denom_new}$'
                                            else:
                                                equation8a = f'$x = {negb}/{twoa} + {out_rad}i \sqrt( {in_rad} )$'
                                                equation8b = f'$x = {negb}/{twoa} - {out_rad}i \sqrt( {in_rad} )$'
                                        else:
                                            if denom!=1:
                                                equation8a = f'$x = {negb}/{twoa} + i \sqrt( {in_rad} ) / {denom_new}$'
                                                equation8b = f'$x = {negb}/{twoa} - i \sqrt( {in_rad} ) / {denom_new}$'
                                            else:
                                                equation8a = f'$x = {negb}/{twoa} + i \sqrt( {in_rad} )$'
                                                equation8b = f'$x = {negb}/{twoa} - i \sqrt( {in_rad} )$'
                                    else:
                                        if out_rad!=1:
                                            if denom!=1:
                                                equation8a = f'$x = {negb}/{twoa} + {out_rad}i / {denom_new}$'
                                                equation8b = f'$x = {negb}/{twoa} - {out_rad}i / {denom_new}$'
                                            else:
                                                equation8a = f'$x = {negb}/{twoa} + {out_rad}i$'
                                                equation8b = f'$x = {negb}/{twoa} - {out_rad}i$'
                                        else:
                                            if denom!=1:
                                                equation8a = f'$x = {negb}/{twoa} + i / {denom_new}$'
                                                equation8b = f'$x = {negb}/{twoa} - i / {denom_new}$'
                                            else:
                                                equation8a = f'$x = {negb}/{twoa} + i$'
                                                equation8b = f'$x = {negb}/{twoa} - i$'


                                    options = list(range(1,21))
                                    if twoa>20: options.append(twoa)
                                    if denom_new>twoa: options.append(denom_new)
                                    denom_new_in = st.selectbox('What goes in the denominator under the radical?',['SELECT' + options])
                                    if denom_new_in=='SELECT': 
                                        st.write()
                                    elif denom_new_in!=denom_new: 
                                        st.write('Try again.')
                                    else:
                                        st.write('Awesome! Our equations are: ' + equation8a + ' and ' + equation8b + '.')
                                        numer1, denom1 = simplify_fraction(negb,twoa)
                                        numer2, denom2 = simplify_fraction(out_rad,denom_new)
                                        if numer1!=negb:
                                            st.write('Simplify the first fraction:')
                                            n1_in = st.selectbox('new numerator',['SELECT' + options])
                                            d1_in = st.selectbox('new denominator',['SELECT' + options])
                                        else:
                                            n1_in = numer1
                                            d1_in = denom1
                                        if numer2!=out_rad:
                                            st.write('Simplify the second fraction:')
                                            n2_in = st.selectbox('new numerator ',['SELECT' + options])
                                            d2_in = st.selectbox('new denominator ',['SELECT' + options])
                                        else:
                                            n2_in = numer2
                                            d2_in = denom2
                                        if (n1_in=='SELECT') or (d1_in=='SELECT') or (n2_in=='SELECT') or (d2_in=='SELECT'):
                                            st.write()
                                        elif (n1_in!=numer1) or (d1_in!=denom1) or (n2_in!=np.abs(numer2)) or (d2_in!=denom2):
                                            st.write('Try again.')
                                        else:
                                            st.write('You did it!')
                                            if denom1>1:
                                                if denom2>1:
                                                    if np.abs(numer2)>1:
                                                        equation9a = f'$x = {numer1}/{denom1} + {np.abs(numer2)}i \sqrt( {in_rad} ) / {denom2}$'
                                                        equation9b = f'$x = {numer1}/{denom1} - {np.abs(numer2)}i \sqrt( {in_rad} ) / {denom2}$'
                                                    else:
                                                        equation9a = f'$x = {numer1}/{denom1} + i \sqrt( {in_rad} ) / {denom2}$'
                                                        equation9b = f'$x = {numer1}/{denom1} - i \sqrt( {in_rad} ) / {denom2}$'
                                                else:
                                                    if np.abs(numer2)>1:
                                                        equation9a = f'$x = {numer1}/{denom1} + {np.abs(numer2)}i \sqrt( {in_rad} )$'
                                                        equation9b = f'$x = {numer1}/{denom1} - {np.abs(numer2)}i \sqrt( {in_rad} )$'
                                                    else:
                                                        equation9a = f'$x = {numer1}/{denom1} + i \sqrt( {in_rad} )$'
                                                        equation9b = f'$x = {numer1}/{denom1} - i \sqrt( {in_rad} )$'
                                            else:
                                                if denom2>1:
                                                    if np.abs(numer2)>1:
                                                        equation9a = f'$x = {numer1} + {np.abs(numer2)}i \sqrt( {in_rad} ) / {denom2}$'
                                                        equation9b = f'$x = {numer1} - {np.abs(numer2)}i \sqrt( {in_rad} ) / {denom2}$'
                                                    else:
                                                        equation9a = f'$x = {numer1} + i \sqrt( {in_rad} ) / {denom2}$'
                                                        equation9b = f'$x = {numer1} - i \sqrt( {in_rad} ) / {denom2}$'
                                                else:
                                                    if np.abs(numer2)>1:
                                                        equation9a = f'$x = {numer1} + {np.abs(numer2)}i \sqrt( {in_rad} )$'
                                                        equation9b = f'$x = {numer1} - {np.abs(numer2)}i \sqrt( {in_rad} )$'
                                                    else:
                                                        equation9a = f'$x = {numer1} + i \sqrt( {in_rad} )$'
                                                        equation9b = f'$x = {numer1} - i \sqrt( {in_rad} )$'
                                            st.write(equation9a + ' and ' + equation9b)
                                            st.balloons()

                    if disc == 0:
                        st.write('But, the discriminant is zero, and plus or minus the square root of zero gives only one answer: zero.')

                        st.write(f'x = [ {negb} + 0] / {twoa} = {negb}/{twoa} and x = [ {negb} - 0] / {twoa} = {negb}/{twoa}')

                        numer1, denom1 = simplify_fraction(negb,twoa)

                        if numer1!=negb:
                            st.write('You can siplify that fraction, though:')
                            st.write(f'{negb}/{twoa} = [ ]/[ ]')
                            n1_in = st.selectbox('New numerator = ',['SELECT'] + list(range(-10,11)))
                            d1_in = st.selectbox('New denominator = ',['SELECT'] + list(range(0,21)))
                            if (n1_in=='SELECT') or (d1_in=='SELECT'):
                                st.write()
                            elif (n1_in!=numer1) or (d1_in!=denom1):
                                st.write('Try again.')
                            else:
                                st.write('You rocked that!')
                                st.write(f'x = {numer1}/{denom1}')
                                st.balloons()
                        else:
                            st.write(f'So the answer is just x = {numer1}/{denom1}; you are all done!')
                            st.balloons()

                    if disc > 0:
                        st.write('The discriminant is positive, so there are 2 REAL solutions.')

                        out_rad, in_rad, denom = simplify_radical(disc)

                        if (out_rad!=None) and (in_rad!=disc):

                            st.write('Can you simplify the radical? You will probably need some scratch paper!')
                            out_str = f'$\sqrt({disc}) = [ ] \sqrt( [ ] )/ [ ]$'
                            st.write(out_str)
                            choices = list(range(1,21))
                            if out_rad>20: choices.append(out_rad)
                            if in_rad>max([out_rad, 20]):  choices.append(in_rad)
                            if denom>max([20, out_rad, in_rad]): choices.append(denom)
                            out1 = st.selectbox('First blank = ',['SELECT'] + choices)
                            in1  = st.selectbox('Second blank = ',['SELECT'] + choices)
                            den1 = st.selectbox('Last blank = ',['SELECT'] + choices)
                            if (out1=='SELECT') or (in1=='SELECT') or (den1=='SELECT'):
                                st.write()
                            elif (out1!=out_rad) or (in1!=in_rad) or (den1!=denom):
                                st.write('Try again.')
                            else:
                                st.write(f'Good! So now (separating the two parts of the fraction) we have: $x = {negb}/{twoa} \pm {out_rad} \sqrt( {in_rad} ) / [ ]$')
                                denom_new = denom*twoa

                                if in_rad!=1:
                                    if out_rad!=1:
                                        if denom_new!=1:
                                            equation8a = f'$x = {negb}/{twoa} + {out_rad} \sqrt( {in_rad} ) / {denom_new}$'
                                            equation8b = f'$x = {negb}/{twoa} - {out_rad} \sqrt( {in_rad} ) / {denom_new}$'
                                        else:    
                                            equation8a = f'$x = {negb}/{twoa} + {out_rad} \sqrt( {in_rad} )$'
                                            equation8b = f'$x = {negb}/{twoa} - {out_rad} \sqrt( {in_rad} )$'
                                    else:
                                        if denom_new!=1:
                                            equation8a = f'$x = {negb}/{twoa} + 1 \sqrt( {in_rad} ) / {denom_new}$'
                                            equation8b = f'$x = {negb}/{twoa} - 1 \sqrt( {in_rad} ) / {denom_new}$'
                                        else:    
                                            equation8a = f'$x = {negb}/{twoa} + 1 \sqrt( {in_rad} )$'
                                            equation8b = f'$x = {negb}/{twoa} - 1 \sqrt( {in_rad} )$'
                                else:
                                    if out_rad!=1:
                                        if denom_new!=1:
                                            equation8a = 'x = ' + f'{negb}/{twoa} + {out_rad} / {denom_new}'
                                            equation8b = 'x = ' + f'{negb}/{twoa} - {out_rad} / {denom_new}'
                                        else:    
                                            equation8a = 'x = ' + f'{negb}/{twoa} + {out_rad}'
                                            equation8b = 'x = ' + f'{negb}/{twoa} - {out_rad}'
                                    else:
                                        if denom_new!=1:
                                            equation8a = 'x = ' + f'{negb}/{twoa} + 1 / {denom_new}'
                                            equation8b = 'x = ' + f'{negb}/{twoa} - 1 / {denom_new}'
                                        else:    
                                            equation8a = 'x = ' + f'{negb}/{twoa} + 1'
                                            equation8b = 'x = ' + f'{negb}/{twoa} - 1'

                                options = list(range(1,21))
                                if denom_new > 20: options.append(denom_new)
                                denom_new_in = st.selectbox('What goes in the denominator under the radical?',['SELECT'] + options)
                                if denom_new_in=='SELECT': 
                                    st.write()
                                elif denom_new_in!=denom_new: 
                                    st.write('Try again.')
                                else:
                                    st.write('Awesome! Our equations are: ' + equation8a + ' and ' + equation8b + '.')

                                    numer1, denom1 = simplify_fraction(negb,twoa)
                                    if numer1!=negb:
                                        st.write('Simplify the first fraction:')
                                        n1_in = st.selectbox('new numerator',['SELECT'] + coef_options)
                                        d1_in = st.selectbox('new denominator',['SELECT'] + coef_options)
                                    else:
                                        n1_in = numer1
                                        d1_in = denom1

                                    numer2, denom2 = simplify_fraction(out_rad,denom_new)
                                    if numer2!=out_rad:
                                        st.write('Simplify the second fraction:')
                                        n2_in = st.selectbox('new numerator ',['SELECT'] + coef_options)
                                        d2_in = st.selectbox('new denominator ',['SELECT'] + coef_options)
                                    else:
                                        n2_in = numer2
                                        d2_in = denom2
                                    if (n1_in=='SELECT') or (d1_in=='SELECT') or (n2_in=='SELECT') or (d2_in=='SELECT'):
                                        st.write()
                                    elif (n1_in!=numer1) or (d1_in!=denom1) or (n2_in!=np.abs(numer2)) or (d2_in!=denom2):
                                        st.write('Try again.')
                                    else:
                                        st.write('You did it!')
                                        if in_rad!=1:
                                            if denom1>1:
                                                if denom2>1:
                                                    if np.abs(numer2)>1:
                                                        equation9a = f'$x = {numer1}/{denom1} + {np.abs(numer2)} \sqrt( {in_rad} ) / {denom2}$'
                                                        equation9b = f'$x = {numer1}/{denom1} - {np.abs(numer2)} \sqrt( {in_rad} ) / {denom2}$'
                                                    else:
                                                        equation9a = f'$x = {numer1}/{denom1} + \sqrt( {in_rad} ) / {denom2}$'
                                                        equation9b = f'$x = {numer1}/{denom1} - \sqrt( {in_rad} ) / {denom2}$'
                                                else:
                                                    if np.abs(numer2)>1:
                                                        equation9a = f'$x = {numer1}/{denom1} + {np.abs(numer2)} \sqrt( {in_rad} )$'
                                                        equation9b = f'$x = {numer1}/{denom1} - {np.abs(numer2)} \sqrt( {in_rad} )$'
                                                    else:
                                                        equation9a = f'$x = {numer1}/{denom1} + \sqrt( {in_rad} )$'
                                                        equation9b = f'$x = {numer1}/{denom1} - \sqrt( {in_rad} )$'
                                            else:
                                                if denom2>1:
                                                    if np.abs(numer2)>1:
                                                        equation9a = f'$x = {numer1} + {np.abs(numer2)} \sqrt( {in_rad} ) / {denom2}$'
                                                        equation9b = f'$x = {numer1} - {np.abs(numer2)} \sqrt( {in_rad} ) / {denom2}$'
                                                    else:
                                                        equation9a = f'$x = {numer1} + \sqrt( {in_rad} ) / {denom2}$'
                                                        equation9b = f'$x = {numer1} - \sqrt( {in_rad} ) / {denom2}$'
                                                else:
                                                    if np.abs(numer2)>1:
                                                        equation9a = f'$x = {numer1} + {np.abs(numer2)} \sqrt( {in_rad} )$'
                                                        equation9b = f'$x = {numer1} - {np.abs(numer2)} \sqrt( {in_rad} )$'
                                                    else:
                                                        equation9a = f'$x = {numer1} + \sqrt( {in_rad} )$'
                                                        equation9b = f'$x = {numer1} - \sqrt( {in_rad} )$'
                                        else:
                                            if denom1>1:
                                                if denom2>1:
                                                    if np.abs(numer2)>1:
                                                        equation9a = 'x = ' + combine_string(f'{numer1}/{denom1} + {np.abs(numer2)}/{denom2}') 
                                                        equation9b = 'x = ' + combine_string(f'{numer1}/{denom1} - {np.abs(numer2)}/{denom2}') + ' (after adding the fractions)'
                                                    else:
                                                        equation9a = 'x = ' + combine_string(f'{numer1}/{denom1} + 1/{denom2}') 
                                                        equation9b = 'x = ' + combine_string(f'{numer1}/{denom1} - 1/{denom2}') + ' (after adding the fractions)'
                                                else:
                                                    if np.abs(numer2)>1:
                                                        equation9a = 'x = ' + combine_string(f'{numer1}/{denom1} + {np.abs(numer2)}') 
                                                        equation9b = 'x = ' + combine_string(f'{numer1}/{denom1} - {np.abs(numer2)}') + ' (after adding the fractions)'
                                                    else:
                                                        equation9a = 'x = ' + combine_string(f'{numer1}/{denom1} + 1') 
                                                        equation9b = 'x = ' + combine_string(f'{numer1}/{denom1} - 1') + ' (after adding the fractions)'
                                            else:
                                                if denom2>1:
                                                    if np.abs(numer2)>1:
                                                        equation9a = 'x = ' + combine_string(f'{numer1} + {np.abs(numer2)}/{denom2}') 
                                                        equation9b = 'x = ' + combine_string(f'{numer1} - {np.abs(numer2)}/{denom2}') + ' (after adding the fractions)'
                                                    else:
                                                        equation9a = 'x = ' + combine_string(f'{numer1} + 1/{denom2}') 
                                                        equation9b = 'x = ' + combine_string(f'{numer1} - 1/{denom2}') + ' (after adding the fractions)'
                                                else:
                                                    if np.abs(numer2)>1:
                                                        equation9a = 'x = ' + combine_string(f'{numer1} + {np.abs(numer2)}') 
                                                        equation9b = 'x = ' + combine_string(f'{numer1} - {np.abs(numer2)}') + ' (after adding the fractions)'
                                                    else:
                                                        equation9a = 'x = ' + combine_string(f'{numer1} + 1')
                                                        equation9b = 'x = ' + combine_string(f'{numer1} - 1') + ' (after adding the fractions)'

                                            st.write(equation9a + ' and ' + equation9b)
                                            st.balloons()
                        if in_rad==disc:
                            
                            equation9a = f'${negb}/{twoa} + \sqrt({disc})/{twoa}$'
                            equation9b = f'${negb}/{twoa} - \sqrt({disc})/{twoa}$'
                            st.write('That square root cannot be simplified, so we just have ' + equation9a + ' and ' + equation9b)
                            numer1, denom1 = simplify_fraction(negb,twoa)
                            if numer1!=negb:
                                st.write('Simplify that first fraction:')
                                n1_in = st.selectbox('new numerator',['SELECT'] + coef_options)
                                d1_in = st.selectbox('new denominator',['SELECT'] + coef_options)
                            else:
                                n1_in = numer1
                                d1_in = denom1

                            if (n1_in=='SELECT') or (d1_in=='SELECT') :
                                st.write()
                            elif (n1_in!=numer1) or (d1_in!=denom1) :
                                st.write('Try again.')
                            else:
                                st.write('You did it!')
                                st.balloons()

############################################### EQUATION IN FACTORED FORM ###############################################
############################################### SOLVE BY FACTORING ONLY ###############################################
    
    if Q1 == 'Factored':
        st.write('a(bx + c)(dx + e) = 0')
        st.write('Select values in the sidebar')
        
        coef_options = list(range(-10,11))
        coef_options_pos = list(range(1,11))
        coef_options_a = list(range(-10,0)) + list(range(1,11))
        a = st.sidebar.selectbox('Enter "a":',['SELECT'] + coef_options_a)
        b = st.sidebar.selectbox('Enter "b":',['SELECT'] + coef_options_pos)
        c = st.sidebar.selectbox('Enter "c":',['SELECT'] + coef_options)
        d = st.sidebar.selectbox('Enter "d":',['SELECT'] + coef_options_pos)
        e = st.sidebar.selectbox('Enter "e":',['SELECT'] + coef_options)

        st.write('')
        
        if (a=='SELECT') or (b=='SELECT') or (c=='SELECT') or (d=='SELECT') or (e=='SELECT'):
            st.write()
        elif c==0: 
            if e==0: 
                gcf = f'{a*b*d}x^2'
                factorlist = [gcf]
                equations = [gcf+ ' = 0']
                solutions = [0]
            else: 
                gcf = f'{a*b}x'
                factorlist = [gcf]
                equations = [gcf + ' = 0']
                solutions = [0]                
                if e>0:
                    factor1 = f'({d}x + {e})'
                    factorlist.append(factor1)
                    equations.append(factor1 + ' = 0')
                    solutions.append(-1*e/d)
                else:
                    factor1 = f'({d}x - {-1*e})'
                    factorlist.append(factor1)
                    equations.append(factor1 + ' = 0')
                    solutions.append(-1*e/d)
 
        elif e==0:
            gcf = f'{a*d}x'
            factorlist = [gcf]
            equations = [gcf + ' = 0']
            solutions = [0]                
            if c>0:
                factor1 = f'({b}x + {c})'
                factorlist.append(factor1)
                equations.append(factor1 + ' = 0')
                solutions.append(-1*c/b)
            else:
                factor1 = f'({b}x - {-1*c})'
                factorlist.append(factor1)
                equations.append(factor1 + ' = 0')
                solutions.append(-1*c/b)
        else:
            gcf = f'{a}'
            if c>0:
                factor1 = f'({b}x + {c})'
            else: 
                factor1 = f'({b}x - {-1*c})' 
            if e>0:
                factor2 = f'({d}x + {e})'
            else:
                factor2 = f'({d}x - {-1*e})'
            factorlist = [gcf+factor1, factor2]
            equations = [factor1 + ' = 0', factor2 + ' = 0']
            solutions = [-1*c/b, -1*e/d]
            
        if (a=='SELECT') or (b=='SELECT') or (c=='SELECT') or (d=='SELECT') or (e=='SELECT'):
            st.write()
        else:
            equation = factorlist[0]
            if len(factorlist)>1: equation += factorlist[1]
            equation += ' = 0'
            st.write(equation)
            N = len(equations)
            if N>1:
                if equations[1]==equations[0]: N=1
            st.write(f'Since the only way to multiply factors to get zero is if at least one of them is equal to zero, this gives us {N} equations:')
            solution_choices = solutions + [c/b, e/d, c, e, -1*c, -1*e, c*b, d*e, -1*c*b, -1*d*e]
            solution_choices = [int(s) if s%1==0 else s for s in solution_choices]
            solution_choices = [np.round(s,4) for s in solution_choices]
            solution_choices = list({s for s in solution_choices})
            solution_choices.sort()

            solutions = [np.round(s,4) for s in solutions]
            solutions = [int(s) if s%1==0 else s for s in solutions]

            if N==1:
                soln1_in = st.selectbox('Solve '+ equations[0],['SELECT'] + solution_choices)
                if soln1_in=='SELECT':
                    st.write()
                elif soln1_in!=solutions[0]:
                    st.write('Try again.')
                else:
                    st.write('You did it!')
                    st.balloons()
            else:
                soln1_in = st.selectbox('Solve '+ equations[0],['SELECT'] + solution_choices)
                soln2_in = st.selectbox('Solve '+ equations[1],['SELECT'] + solution_choices)
                if (soln1_in=='SELECT') or (soln2_in=='SELECT'):
                    st.write()
                elif (soln1_in!=solutions[0]) or (soln2_in!=solutions[1]):
                    st.write('Try again.')
                else:
                    st.write('You did it!')
                    st.balloons()

############################################### EQUATION IN VERTEX FORM ###############################################
############################################### SOLVE BY COMPLETING THE SQUARE ONLY ###############################################
        
    if Q1 == 'Vertex':
        st.latex('a(x-h)^2 + k = 0')
        
        st.write('Select values in the sidebar')
        
        coef_options = list(range(-10,11))
        a_options = list(range(-10,0))+list(range(1,11))
        a = st.sidebar.selectbox('Enter "a":',['SELECT'] + a_options)
        h = st.sidebar.selectbox('Enter "h":',['SELECT'] + coef_options)
        k = st.sidebar.selectbox('Enter "k":',['SELECT'] + coef_options)

        st.write('')
        
        if (a!='SELECT') and (h!='SELECT') and (k!='SELECT'):
            
            if a==1: 
                if h>0:
                    if k>0:
                        equation = f'(x - {h})^2 + {k} = 0'
                        equation1 = f'(x - {h})^2  = - {k}'
                    elif k==0:
                        equation = f'(x - {h})^2 = 0'
                        equation1 = f'(x - {h})^2 = 0'
                    else:
                        equation = f'(x - {h})^2 - {-1*k} = 0'
                        equation1 = f'(x - {h})^2 = {-1*k}'

                elif h==0:
                    if k>0:
                        equation = f'x^2 + {k} = 0'
                        equation1 = f'x^2 = -{k}'
                    elif k==0:
                        equation = f'x^2 = 0'
                        equation1 = f'x^2 = 0'
                    else:
                        equation = f'x^2 - {-1*k} = 0'
                        equation1 = f'x^2 = {-1*k}'

                else:
                    if k>0:
                        equation = f'(x + {-1*h})^2 + {k} = 0'
                        equation1 = f'(x + {-1*h})^2 = -{k}'
                    elif k==0:
                        equation = f'(x + {-1*h})^2 = 0'
                        equation1 = f'(x + {-1*h})^2 = 0'
                    else:
                        equation = f'(x + {-1*h})^2 - {-1*k} = 0'
                        equation1 = f'(x + {-1*h})^2 = {-1*k}'

            elif a!=1: 
                if h>0:
                    if k>0:
                        equation = f'{a}(x - {h})^2 + {k} = 0'
                        equation1 = f'{a}(x - {h})^2 = -{k}'
                    elif k==0:
                        equation = f'{a}(x - {h})^2 = 0'
                        equation1 = f'{a}(x - {h})^2 = 0'
                    else:
                        equation = f'{a}(x - {h})^2 - {-1*k} = 0'
                        equation1 = f'{a}(x - {h})^2 = {-1*k}'

                elif h==0:
                    if k>0:
                        equation = f'{a}x^2 + {k} = 0'
                        equation1 = f'{a}x^2 = -{k}'
                    elif k==0:
                        equation = f'{a}x^2 = 0'
                        equation1 = f'{a}x^2 = 0'
                    else:
                        equation = f'{a}x^2 - {-1*k} = 0'
                        equation1 = f'{a}x^2 = {-1*k}'

                else:
                    if k>0:
                        equation = f'{a}(x + {-1*h})^2 + {k} = 0'
                        equation1 = f'{a}(x + {-1*h})^2 = -{k}'
                    elif k==0:
                        equation = f'{a}(x + {-1*h})^2 = 0'
                        equation1 = f'{a}(x + {-1*h})^2 = 0'
                    else:
                        equation = f'{a}(x + {-1*h})^2 - {-1*k} = 0'
                        equation1 = f'{a}(x + {-1*h})^2 = {-1*k}'

            st.latex(equation)
            step1 = False
            if k!=0: 
                st.write('Step 1: Move the constant to the other side')
                rhs_in = st.selectbox('What is the right hand side equal to now?',['SELECT'] + coef_options)
                if rhs_in!='SELECT':
                    if rhs_in!=(-1*k):
                        st.write('Try again.')
                    else:
                        st.write('Good job!')
                        st.latex(equation1)
                        step1 = True
            else:
                st.write('Step 1 is to move the constant to the other side, but since k=0, you can skip that step. Yay!')
                step1 = True
            if step1:
                step2 = False
                if a!=1:
                    st.write('Step 2: Divide by "a".')
                    new_rhs = np.round(-1*k/a,10)
                    if new_rhs%1==0: new_rhs = int(new_rhs)
                    if h!=0:
                        options = list({-1*k/a, k/a, -1*k/h, k/h, -1*h/a, h/a})
                    else:
                        options = list({-1*k/a, k/a, -1*h/a, h/a})

                    options = [c if c!=0 else 0.0 for c in options]
                    options = [int(c) if c%1==0 else np.round(c,10) for c in options]
                    options.sort()
                    new_rhs_in = st.selectbox('What is the right hand side equal to now?',['SELECT'] + options)
                    if new_rhs_in !='SELECT':
                        if new_rhs_in!=new_rhs:
                            st.write('Try again.')
                        else:
                            if h<0:
                                equation2 = f'(x + {-1*h})^2 = {new_rhs}'
                            elif h==0:
                                equation2 = f'x^2 = {new_rhs}'
                            else:
                                equation2 = f'(x - {h})^2 = {new_rhs}'
                            st.write('Good!')
                            step2 = True
                elif a==1:
                    st.write('Step 2 is to divide by "a", but since your a = 1, you can skip that step. Yay!')
                    equation2 = equation1
                    new_rhs = -1*k
                    step2 = True
                if step2:
                    step3 = False
                    st.latex(equation2)
                    st.write('Step 3: Take the square root:')
                    if h<0:
                        equation3 = f'x + {-1*h} = \pm \sqrt( {new_rhs} )'            
                    elif h==0:
                        equation3 = f'x = \pm \sqrt( {new_rhs} )'
                    else:
                        equation3 = f'x - {h} = \pm \sqrt( {new_rhs} )'
                    st.latex(equation3)
                    if new_rhs<0:
                        st.write('Uh oh! There are no REAL numbers that can square to give a negative number.')
                        st.write("If you're in algebra 1 right now, you can stop here - the answer is 'no real solutions'.")
                        st.write("But if you're in algebra 2 or another advanced math class, it's a little trickier.")
                        cont = st.selectbox('Continue on to find the 2 complex solutions?',['SELECT', 'yes', 'no'])
                        if cont=='SELECT':
                            st.write()
                        elif cont == 'no':
                            st.write('OK, good job on this problem!')
                        else:
                            st.write('We know that the square root of -1 is "i". So we can take that out of the square root, and drop the negative:')
                            equation4 = equation3.replace(f'\sqrt( {new_rhs}',f'i \sqrt( {-1*new_rhs}')
                            st.latex(equation4)
                            out_rad, in_rad, denom = simplify_radical(-1*new_rhs)
                            if in_rad!=-1*new_rhs:
                                st.write('Can you simplify the radical? You will probably need some scratch paper!')
                                out_str = f'$\sqrt({-1*new_rhs}) = [ ] \sqrt( [ ] )/ [ ]$'
                                st.write(out_str)
                                choices = list(range(1,201))
                                out1 = st.selectbox('First blank = ',['SELECT'] + choices)
                                in1  = st.selectbox('Second blank = ',['SELECT'] + choices)
                                den1 = st.selectbox('Last blank = ',['SELECT'] + choices)
                                if (out1=='SELECT') or (in1=='SELECT') or (den1=='SELECT'):
                                    st.write()
                                elif (out1!=out_rad) or (in1!=in_rad) or (den1!=denom):
                                    st.write('Try again.')
                                else:
                                    if out_rad==1:
                                        if in_rad==1:
                                            if denom==1:
                                                sqrt_str = 'i'
                                            else:
                                                sqrt_str = f'i / {denom}'
                                        else:
                                            if denom==1:
                                                sqrt_str = f'i \sqrt( {in_rad} )'
                                            else:
                                                sqrt_str = f'i \sqrt( {in_rad} ) / {denom}'
                                    else:
                                        if in_rad==1:
                                            if denom==1:
                                                sqrt_str = f'{out_rad}i'
                                            else:
                                                sqrt_str = f'{out_rad}i / {denom}'
                                        else:
                                            if denom==1:
                                                sqrt_str = f'{out_rad}i \sqrt( {in_rad} )'
                                            else:
                                                sqrt_str = f'{out_rad}i \sqrt( {in_rad} ) / {denom}'
                                    equation5 = equation4.replace(f'i \sqrt( {-1*new_rhs}', sqrt_str)
                                    st.write(f'Good! So now we have: ')
                                    st.latex(equation5)
                                    step3 = True
                            else:
                                equation5 = equation4
                                step3 = True
                            if step3:
                                st.write('Step 4: Almost done! Solve for x.')
                                if h!=0:
                                    soln1 = f'{h} + ' + sqrt_str.replace('\sqrt',' sqrt')
                                    soln2 = f'{h} - ' + sqrt_str.replace('\sqrt',' sqrt')
                                    wrong1= f'{-1*h} + ' + sqrt_str.replace('\sqrt',' sqrt')
                                    wrong2= f'{-1*h} - ' + sqrt_str.replace('\sqrt',' sqrt')
                                    solution_options = [soln1, soln2, wrong1, wrong2]
                                    correct = [soln1, soln2]
                                    solution_options.sort()
                                    sel1 = st.checkbox(solution_options[0])
                                    sel2 = st.checkbox(solution_options[1])
                                    sel3 = st.checkbox(solution_options[2])
                                    sel4 = st.checkbox(solution_options[3])
                                    if   (sel1==True) and (solution_options[0] not in correct): st.write('Try again.')
                                    elif (sel2==True) and (solution_options[1] not in correct): st.write('Try again.')
                                    elif (sel3==True) and (solution_options[2] not in correct): st.write('Try again.')
                                    elif (sel4==True) and (solution_options[3] not in correct): st.write('Try again.')
                                    elif (sel1!=True) and (solution_options[0] in correct): st.write('Try again.')
                                    elif (sel2!=True) and (solution_options[1] in correct): st.write('Try again.')
                                    elif (sel3!=True) and (solution_options[2] in correct): st.write('Try again.')
                                    elif (sel4!=True) and (solution_options[3] in correct): st.write('Try again.')
                                    else:
                                        st.write('You did it!')
                                        st.balloons()
                                elif h==0:
                                    soln1 = sqrt_str.replace('\sqrt',' sqrt')
                                    soln2 = '-' + sqrt_str.replace('\sqrt',' sqrt')
                                    correct = [soln1, soln2]
                                    sel1 = st.checkbox(correct[0])
                                    sel2 = st.checkbox(correct[1])
                                    if (sel1!=True): st.write('Try again.')
                                    elif (sel2!=True): st.write('Try again.')
                                    else:
                                        st.write('You did it!')
                                        st.balloons()

                    elif new_rhs==0:
                        st.write('Step 4: Almost done! Solve for x.')
                        st.write('(The square root of zero is just zero, and -0 = +0, so there is only one solution.)')
                        soln1 = f'{h}'
                        if h!=0:
                            wrong1= f'{-1*h}'
                        else:
                            wrong1= f'{a}'
                        solution_options = [soln1, wrong1]
                        correct = [soln1]
                        solution_options.sort()
                        sel1 = st.checkbox(solution_options[0])
                        sel2 = st.checkbox(solution_options[1])
                        if   (sel1==True) and (solution_options[0] not in correct): st.write('Try again.')
                        elif (sel2==True) and (solution_options[1] not in correct): st.write('Try again.')
                        elif (sel1!=True) and (solution_options[0] in correct): st.write('Try again.')
                        elif (sel2!=True) and (solution_options[1] in correct): st.write('Try again.')
                        else:
                            st.write('You did it!')
                            st.balloons()

                    else:
                        equation4 = equation3
                        out_rad, in_rad, denom = simplify_radical(new_rhs)
                        if in_rad!=new_rhs:
                            st.write('Can you simplify the radical? You will probably need some scratch paper!')
                            out_str = f'$\sqrt({new_rhs}) = [ ] \sqrt( [ ] )/ [ ]$'
                            st.write(out_str)
                            choices = list(range(1,201))
                            out1 = st.selectbox('First blank = ',['SELECT'] + choices)
                            in1  = st.selectbox('Second blank = ',['SELECT'] + choices)
                            den1 = st.selectbox('Last blank = ',['SELECT'] + choices)
                            if (out1=='SELECT') or (in1=='SELECT') or (den1=='SELECT'):
                                st.write()
                            elif (out1!=out_rad) or (in1!=in_rad) or (den1!=denom):
                                st.write('Try again.')
                            else:
                                if out_rad==1:
                                    if in_rad==1:
                                        if denom==1:
                                            sqrt_str = '1'
                                        else:
                                            sqrt_str = f'1 / {denom}'
                                    else:
                                        if denom==1:
                                            sqrt_str = f'sqrt( {in_rad} )'
                                        else:
                                            sqrt_str = f'sqrt( {in_rad} ) / {denom}'
                                else:
                                    if in_rad==1:
                                        if denom==1:
                                            sqrt_str = f'{out_rad}'
                                        else:
                                            sqrt_str = f'{out_rad} / {denom}'
                                    else:
                                        if denom==1:
                                            sqrt_str = f'{out_rad} sqrt( {in_rad} )'
                                        else:
                                            sqrt_str = f'{out_rad} sqrt( {in_rad} ) / {denom}'

                                equation5 = equation4.replace(f'\sqrt( {new_rhs} )', sqrt_str.replace('sqrt','\sqrt'))
                                st.write(f'Good! So now we have: ')
                                st.latex(equation5)
                                step3 = True
                        else:
                            equation5 = equation4
                            sqrt_str = f' sqrt( {new_rhs} )'
                            step3 = True
                        if step3:
                            st.write('Step 4: Almost done! Solve for x by selecting all CORRECT solutions below.')
                            if h!=0:
                                soln1 = f'{h} + ' + sqrt_str
                                soln2 = f'{h} - ' + sqrt_str

                                wrong1= f'{-1*h} + ' + sqrt_str
                                wrong2= f'{-1*h} - ' + sqrt_str
                                solution_options = [soln1, soln2, wrong1, wrong2]
                                correct = [soln1, soln2]
                                solution_options.sort()
                                sel1 = st.checkbox(solution_options[0])
                                sel2 = st.checkbox(solution_options[1])
                                sel3 = st.checkbox(solution_options[2])
                                sel4 = st.checkbox(solution_options[3])
                                if   (sel1==True) and (solution_options[0] not in correct): st.write('Try again.')
                                elif (sel2==True) and (solution_options[1] not in correct): st.write('Try again.')
                                elif (sel3==True) and (solution_options[2] not in correct): st.write('Try again.')
                                elif (sel4==True) and (solution_options[3] not in correct): st.write('Try again.')
                                elif (sel1!=True) and (solution_options[0] in correct): st.write('Try again.')
                                elif (sel2!=True) and (solution_options[1] in correct): st.write('Try again.')
                                elif (sel3!=True) and (solution_options[2] in correct): st.write('Try again.')
                                elif (sel4!=True) and (solution_options[3] in correct): st.write('Try again.')
                                else:
                                    st.write('You did it!')
                                    st.balloons()
                            elif h==0:
                                soln1 = sqrt_str
                                soln2 = '-' + sqrt_str
                                correct = [soln1, soln2]
                                sel1 = st.checkbox(correct[0])
                                sel2 = st.checkbox(correct[1])
                                if (sel1!=True): st.write('Try again.')
                                elif (sel2!=True): st.write('Try again.')
                                else:
                                    st.write('You did it!')
                                    st.balloons()

############################################### POLYNOMIAL EQUATIONS SECTION ###############################################

elif eqn_type == 'Polynomial Equations':
    chk3 = False
    degree = st.sidebar.selectbox('What degree?',['Cubic (x^3)', 'Quartic (x^4)', 'Quintic (x^5)'])
    coef_options = list(range(-40,41))
    if degree == 'Quintic (x^5)':
        c5 = st.sidebar.selectbox('Enter the x^5 coefficient:',['SELECT']+coef_options)
        c4 = st.sidebar.selectbox('Enter the x^4 coefficient:',['SELECT']+coef_options)
    elif degree == 'Quartic (x^4)':
        c5 = 0
        c4 = st.sidebar.selectbox('Enter the x^4 coefficient:',['SELECT']+coef_options)
    else:
        c5 = 0
        c4 = 0
    c3 = st.sidebar.selectbox('Enter the x^3 coefficient:',['SELECT']+coef_options)
    c2 = st.sidebar.selectbox('Enter the x^2 coefficient):',['SELECT']+coef_options)
    c1 = st.sidebar.selectbox('Enter the linear coefficient:',['SELECT']+coef_options)
    c0 = st.sidebar.selectbox('Enter the constant:',['SELECT']+coef_options)
    b4 = c4
    b3 = c3
    b2 = c2
    b1 = c1
    b0 = c0
    if (c5!='SELECT') and (c4!='SELECT') and (c3!='SELECT') and (c2!='SELECT') and (c1!='SELECT') and (c0!='SELECT'):

        if c5!=0:
            equation = f'{c5}x^5 + {c4}x^4 + {c3}x^3 + {c2}x^2 + {c1}x + {c0} = 0'
            q = np.abs(c5)
        elif c4!=0:
            equation = f'{c4}x^4 + {c3}x^3 + {c2}x^2 + {c1}x + {c0} = 0'
            q = np.abs(c4)
        else:
            equation = f'{c3}x^3 + {c2}x^2 + {c1}x + {c0} = 0'
            q = np.abs(c3)
        if c0!=0:
            p = np.abs(c0)
        elif c1!=0:
            p = np.abs(c1)
        elif c2!=0:
            p = np.abs(c2)
        elif c3!=0:
            p = np.abs(c3)
        elif c4!=0:
            p = np.abs(c4)
        else:
            p = np.abs(c5)
        # all rational roots of a polynomial equation are in the list +/- [factors of p / factors of q],
        # where p is the constant term and q is the leading coefficient
        st.latex(equation)
        q_list = [j for j in range(1,(q+1)) if q%j==0]
        p_list = [j for j in range(1,(p+1)) if p%j==0]
        rat_root_list = [p1/q1 for q1 in q_list for p1 in p_list]
        rat_root_list += [-1*c for c in rat_root_list]
        # check all the values in the list of possible rational roots for values that make the polynomial equation true. Those are the roots.
        roots = [r for r in rat_root_list if np.round(c5*np.power(r,5)+c4*np.power(r,4)+c3*np.power(r,3)+c2*np.power(r,2)+c1*r+c0,6)==0]
        if c0==0: roots.append(0)
        ## NEED A CHECK FOR MULTIPLICITY!
        new_roots = []
        for r in roots: # check all roots in the list to see it they have multiplicity: e.g., x^3+3x^2+3x+1=0 has a root -1 with m3 because it equals (x+1)^3
            r5,r4,r3,r2,r1,chk0 = synthetic_division(c5,c4,c3,c2,c1,c0,r)
            r5,r4,r3,r2,r1,chk1 = synthetic_division(r5,r4,r3,r2,r1,chk0,r)
            r5,r4,r3,r2,r1,chk2 = synthetic_division(r5,r4,r3,r2,r1,chk1,r)
            if (chk1==0): 
                new_roots.append(r) # if chk1==0, then the same root works at least twice -- append another copy of it to the root list
            if (chk2==0):
                new_roots.append(r) # if chk2==0, then the same root works at least 3 times -- append a 3rd copy to the list
        roots = roots + new_roots
        
        # Do we have enough rational roots to be able to solve the selected equation? If not alert the user to adjust choices.
        if ((c5!=0) and (len(roots)<3)):
            st.write('For a quintic equation, you need to have at least 3 rational roots (from the $\pm$ p/q list).')
            if len(roots)<1:
                st.write('This equation has none; please change your selections in the sidebar to get a solvable equation.')
            else:
                st.write(f'This equation only has {len(roots)}; please change your selections in the sidebar to get a solvable equation.')
        elif ((c4!=0) and (len(roots)<2)):
            st.write('For a quartic equation, you need to have at least 2 rational roots (from the $\pm$ p/q list).')
            if len(roots)<1:
                st.write('This equation has none; please change your selections in the sidebar to get a solvable equation.')
            else:
                st.write(f'This equation only has {len(roots)}; please change your selections in the sidebar to get a solvable equation.')
        elif (len(roots)<1):
            st.write('For a cubic equation, you need to have at least 1 rational roots (from the $\pm$ p/q list).')
            st.write('This equation has none; please change your selections in the sidebar to get a solvable equation.')
        else: # ready to solve
            
            if c5!=0: # we have a quintic (degree = 5) equation
                root = roots[0] # get the first rational root
                if root%1 == 0: # whole number root
                    root = int(root)
                    st.write(f'One rational root is: {root}')
                    st.write('Use synthetic division to reduce this quintic equation to a quartic:')
                    sdiv_df = pd.DataFrame({
                        '0': [f'{root} __|', '', '', ''],
                        '' : [c5, '', '---', '[  ]'],
                        ' ' : [c4, '', '---', '[  ]'],
                        '  ' : [c3, '', '---', '[  ]'],
                        '   ' : [c2, '', '---', '[  ]'],
                        '    ' : [c1, '', '---', '[  ]'],
                        '     ' : [c0, '', '---', ''],
                    })
                    sdiv_df.set_index('0',inplace=True)
                    st.table(sdiv_df)
                    b4 = c5
                    b3 = b4*root + c4
                    b2 = b3*root + c3
                    b1 = b2*root + c2
                    b0 = b1*root + c1
                    b4_in = st.text_input('1st blank',value='') 
                    b3_in = st.text_input('2nd blank',value='')
                    b2_in = st.text_input('3rd blank',value='')
                    b1_in = st.text_input('4th blank',value='')
                    b0_in = st.text_input('5th blank',value='')
                    chk5 = False
                    if (b4_in.isnumeric) and (b3_in.isnumeric) and (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                        b4_in = int(b4_in)
                        b3_in = int(b3_in)
                        b2_in = int(b2_in)
                        b1_in = int(b1_in)
                        b0_in = int(b0_in)
                        if (b4_in!=b4) or (b3_in!=b3) or (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                            st.write('Try again.')
                            chk5 = False
                        else:
                            st.write('Nicely done! We now have a quartic equation:')
                            st.latex(f'{b4}x^4 + {b3}x^3 + {b2}x^2 + {b1}x + {b0} = 0.')
                            chk5 = True # set flag to indicate we are goot to continue with the quartic
                else: # fraction root
                    numer, denom = decimal_to_fraction(root)
                    st.write(f'One rational root is {root}, or {numer}/{denom}.')
                    st.write('Even though this is a fraction, we can still use synthetic division to reduce this quintic equation to a quartic;')
                    st.write(f' we just have to divide by {denom} at the end.')
                    sdiv_df = pd.DataFrame({
                        '0': [f'{root} __|', '', '', ''],
                        '' : [c5, '', '---', '[  ]'],
                        ' ' : [c4, '', '---', '[  ]'],
                        '  ' : [c3, '', '---', '[  ]'],
                        '   ' : [c2, '', '---', '[  ]'],
                        '    ' : [c1, '', '---', '[  ]'],
                        '     ' : [c0, '', '---', ''],
                    })
                    sdiv_df.set_index('0',inplace=True)
                    st.table(sdiv_df)
                    b4 = c5
                    b3 = b4*root + c4
                    b2 = b3*root + c3
                    b1 = b2*root + c2
                    b0 = b1*root + c1
                    b4_in = st.text_input('1st blank',value = '')
                    b3_in = st.text_input('2nd blank',value = '')
                    b2_in = st.text_input('3rd blank',value = '')
                    b1_in = st.text_input('4th blank',value = '')
                    b0_in = st.text_input('5th blank',value = '')
                    if (b4_in.isnumeric) and (b3_in.isnumeric) and (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                        b4_in = int(b4_in)
                        b3_in = int(b3_in)
                        b2_in = int(b2_in)
                        b1_in = int(b1_in)
                        b0_in = int(b0_in)
                        if (b4_in!=b4) or (b3_in!=b3) or (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                            st.write('Try again.')
                            chk5 = False
                        else:
                            b4 = int(b4/denom)
                            b3 = int(b3/denom)
                            b2 = int(b2/denom)
                            b1 = int(b1/denom)
                            b0 = int(b0/denom)
                            st.write(f'Nicely done! After dividing those all by {denom}, we have a quartic equation:')
                            st.latex(f'{b4}x^4 + {b3}x^3 + {b2}x^2 + {b1}x + {b0} = 0.')
                            chk5 = True # set flag that we are good to continue with the quartic
                if chk5==True: # continue with the quartic
                    c4 = b4 # reset coefficients
                    c3 = b3
                    c2 = b2
                    c1 = b1
                    c0 = b0
                    root = roots[1] # get the next root
                    if root==0: # check to see if the root is zero. 
                        st.write(f'Another rational root is 0. So we can just divide the equation by x:')
                        b3 = c4
                        b2 = c3
                        b1 = c2
                        b0 = c1
                        st.write('We now have a cubic equation:')
                        st.latex(f'{b3}x^3 + {b2}x^2 + {b1}x + {b0} = 0.')
                        chk4 = True
                    elif root%1 == 0: # whole number root
                        root = int(root)
                        st.write(f'Another rational root is: {root}')
                        st.write('Use synthetic division to reduce this quartic equation to a cubic:')
                        sdiv_df = pd.DataFrame({
                            '0': [f'{root} __|', '', '', ''],
                            ' ' : [c4, '', '---', '[  ]'],
                            '  ' : [c3, '', '---', '[  ]'],
                            '   ' : [c2, '', '---', '[  ]'],
                            '    ' : [c1, '', '---', '[  ]'],
                            '     ' : [c0, '', '---', ''],
                        })
                        sdiv_df.set_index('0',inplace=True)
                        st.table(sdiv_df)
                        b3 = c4
                        b2 = b3*root + c3
                        b1 = b2*root + c2
                        b0 = b1*root + c1
                        b3_in = st.text_input(' 1st blank',value = '')
                        b2_in = st.text_input(' 2nd blank',value = '')
                        b1_in = st.text_input(' 3rd blank',value = '')
                        b0_in = st.text_input(' 4th blank',value = '')
                        if (b3_in.isnumeric) and (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                            b3_in = int(b3_in)
                            b2_in = int(b2_in)
                            b1_in = int(b1_in)
                            b0_in = int(b0_in)
                            if (b3_in!=b3) or (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                st.write('Try again.')
                                chk4 = False
                            else:
                                st.write(f'Nicely done! We now have a cubic equation:')
                                st.latex(f'{b3}x^3 + {b2}x^2 + {b1}x + {b0} = 0.')
                                chk4 = True
                    else: # fraction root
                        numer, denom = decimal_to_fraction(root)
                        st.write(f'Another rational root is {root}, or {numer}/{denom}.')
                        st.write('Even though this is a fraction, we can still use synthetic division to reduce this quartic equation to a cubic;')
                        st.write(f' we just have to divide by {denom} at the end.')
                        sdiv_df = pd.DataFrame({
                            '0': [f'{root} __|', '', '', ''],
                            ' ' : [c4, '', '---', '[  ]'],
                            '  ' : [c3, '', '---', '[  ]'],
                            '   ' : [c2, '', '---', '[  ]'],
                            '    ' : [c1, '', '---', '[  ]'],
                            '     ' : [c0, '', '---', ''],
                        })
                        sdiv_df.set_index('0',inplace=True)
                        b3 = c4
                        b2 = b3*root + c3
                        b1 = b2*root + c2
                        b0 = b1*root + c1
                        chk4 = False
                        b3_in = st.text_input(' 1st blank',value = '')
                        b2_in = st.text_input(' 2nd blank',value = '')
                        b1_in = st.text_input(' 3rd blank',value = '')
                        b0_in = st.text_input(' 4th blank',value = '')
                        if (b3_in.isnumeric) and (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                            b3_in = int(b3_in)
                            b2_in = int(b2_in)
                            b1_in = int(b1_in)
                            b0_in = int(b0_in)
                            if (b3_in!=b3) or (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                st.write()
                                chk4 = False
                            else:
                                b3 = int(b3/denom)
                                b2 = int(b2/denom)
                                b1 = int(b1/denom)
                                b0 = int(b0/denom)
                                st.write(f'Nicely done! After dividing those all by {denom}, we have a cubic equation:')
                                st.latex(f'{b3}x^3 + {b2}x^2 + {b1}x + {b0} = 0.')
                                chk4 = True # set the flag that we are good to continue with the cubic

                    if chk4==True: # continue
                        c3 = b3 # reset coefficients
                        c2 = b2
                        c1 = b1
                        c0 = b0
                        root = roots[2] # get the next root
                        if root==0: # check to see if the root is zero. 
                            st.write(f'Another rational root is 0. So we can just divide the equation by x:')
                            b2 = c3
                            b1 = c2
                            b0 = c1
                            st.write('We now have a quadratic equation:')
                            st.latex(f'{b2}x^2 + {b1}x + {b0} = 0.')
                            chk3 = True

                        elif (root%1 == 0): # whole number root
                            root = int(root)
                            st.write(f'Another rational root is: {root}')
                            st.write('Use synthetic division to reduce this cubic equation to a quadratic:')
                            sdiv_df = pd.DataFrame({
                                '0': [f'{root} __|', '', '', ''],
                                '  ' : [c3, '', '---', '[  ]'],
                                '   ' : [c2, '', '---', '[  ]'],
                                '    ' : [c1, '', '---', '[  ]'],
                                '     ' : [c0, '', '---', ''],
                            })
                            sdiv_df.set_index('0',inplace=True)
                            st.table(sdiv_df)
                            b2 = c3
                            b1 = b2*root + c2
                            b0 = b1*root + c1
                            chk3 = False
                            b2_in = st.text_input(' 1st blank ',value = '')
                            b1_in = st.text_input(' 2nd blank ',value = '')
                            b0_in = st.text_input(' 3rd blank ',value = '')
                            if (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                                b2_in = int(b2_in)
                                b1_in = int(b1_in)
                                b0_in = int(b0_in)
                                if (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                    st.write('Try again.')
                                    chk3 = False
                                else:
                                    st.write('Nicely done! We now have a quadratic equation:')
                                    st.latex(f'{b2}x^2 + {b1}x + {b0} = 0.')
                                    chk3 = True
                        elif (root%1!=0): # fraction root
                            numer, denom = decimal_to_fraction(root)
                            st.write(f'Another rational root is {root}, or {numer}/{denom}.')
                            st.write('Even though this is a fraction, we can still use synthetic division to reduce this cubic equation to a quadratic;')
                            st.write(f' we just have to divide by {denom} at the end.')
                            sdiv_df = pd.DataFrame({
                                '0': [f'{root} __|', '', '', ''],
                                '  ' : [c3, '', '---', '[  ]'],
                                '   ' : [c2, '', '---', '[  ]'],
                                '    ' : [c1, '', '---', '[  ]'],
                                '     ' : [c0, '', '---', ''],
                            })
                            sdiv_df.set_index('0',inplace=True)
                            st.table(sdiv_df)
                            b2 = c3
                            b1 = b2*root + c2
                            b0 = b1*root + c1
                            chk3 = False
                            b2_in = st.text_input(' 1st blank ',value = '')
                            b1_in = st.text_input(' 2nd blank ',value = '')
                            b0_in = st.text_input(' 3rd blank ',value = '')
                            if (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                                b2_in = int(b2_in)
                                b1_in = int(b1_in)
                                b0_in = int(b0_in)
                                if (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                    st.write('Try again.')
                                    chk3 = False
                                else:
                                    b2 = int(b2/denom)
                                    b1 = int(b1/denom)
                                    b0 = int(b0/denom)
                                    st.write(f'Nicely done! After dividing those all by {denom}, we have a quadratic equation:')
                                    st.latex(f'{b2}x^2 + {b1}x + {b0} = 0.')
                                    chk3 = True # set flag that we are good to continue with cubic

            elif c4!=0: # starting with a quartic equation (degree = 4)
                chk5 = True
                if chk5==True:
                    chk4 = False
                    root = roots[0] # get first root
                    if root==0: # check for root = 0
                        st.write(f'Another rational root is 0. So we can just divide the equation by x:')
                        b3 = c4
                        b2 = c3
                        b1 = c2
                        b0 = c1
                        st.write('We now have a cubic equation:')
                        st.latex(f'{b3}x^3 + {b2}x^2 + {b1}x + {b0} = 0.')
                        chk4 = True # set flag that we are good to continue with cubic
                    elif root%1 == 0: # whole number root
                        root = int(root)
                        st.write(f'One rational root is: {root}')
                        st.write('Use synthetic division to reduce this quartic equation to a cubic:')
                        sdiv_df = pd.DataFrame({
                            '0': [f'{root} __|', '', '', ''],
                            ' ' : [c4, '', '---', '[  ]'],
                            '  ' : [c3, '', '---', '[  ]'],
                            '   ' : [c2, '', '---', '[  ]'],
                            '    ' : [c1, '', '---', '[  ]'],
                            '     ' : [c0, '', '---', ''],
                        })
                        sdiv_df.set_index('0',inplace=True)
                        st.table(sdiv_df)
                        b3 = c4
                        b2 = b3*root + c3
                        b1 = b2*root + c2
                        b0 = b1*root + c1
                        chk4 = False
                        b3_in = st.text_input(' 1st blank', value = '')
                        b2_in = st.text_input(' 2nd blank', value = '')
                        b1_in = st.text_input(' 3rd blank', value = '')
                        b0_in = st.text_input(' 4th blank', value = '')
                    
                        if (b3_in.isnumeric) and (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):      
                            b3_in = int(b3_in)
                            b2_in = int(b2_in)
                            b1_in = int(b1_in)
                            b0_in = int(b0_in)
                            if (b3_in!=b3) or (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                st.write('Try again.')
                                chk4 = False
                            else:
                                st.write('Nicely done! We now have a cubic equation:')
                                st.latex(f'{b3}x^3 + {b2}x^2 + {b1}x + {b0} = 0.')
                                chk4 = True # set flag that we are good to continue with the cubic
                    else: # fraction root
                        numer, denom = decimal_to_fraction(root)
                        st.write(f'One rational root is {root}, or {numer}/{denom}.')
                        st.write('Even though this is a fraction, we can still use synthetic division to reduce this quartic equation to a cubic;')
                        st.write(f' we just have to divide by {denom} at the end.')
                        sdiv_df = pd.DataFrame({
                            '0': [f'{root} __|', '', '', ''],
                            ' ' : [c4, '', '---', '[  ]'],
                            '  ' : [c3, '', '---', '[  ]'],
                            '   ' : [c2, '', '---', '[  ]'],
                            '    ' : [c1, '', '---', '[  ]'],
                            '     ' : [c0, '', '---', ''],
                        })
                        sdiv_df.set_index('0',inplace=True)
                        st.table(sdiv_df)
                        b3 = int(c4)
                        b2 = int(b3*root + c3)
                        b1 = int(b2*root + c2)
                        b0 = int(b1*root + c1)
                        chk4 = False
                        b3_in = st.text_input(' 1st blank', value= '')
                        b2_in = st.text_input(' 2nd blank', value= '')
                        b1_in = st.text_input(' 3rd blank', value= '')
                        b0_in = st.text_input(' 4th blank', value= '')
                         
                        if (b3_in.isnumeric) and (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):        
                            b3_in = int(b3_in)
                            b2_in = int(b2_in)
                            b1_in = int(b1_in)
                            b0_in = int(b0_in)
                            if (b3_in!=b3) or (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                st.write('Try again.')
                                chk4 = False
                            else:
                                b3 = int(b3/denom)
                                b2 = int(b2/denom)
                                b1 = int(b1/denom)
                                b0 = int(b0/denom)
                                st.write(f'Nicely done! After dividing those all by {denom}, we have a cubic equation:')
                                st.latex(f'{b3}x^3 + {b2}x^2 + {b1}x + {b0} = 0.')
                                chk4 = True # set flag that we are good to continue with the cubic

                    if chk4==True: # continue with cubic
                        c3 = b3
                        c2 = b2
                        c1 = b1
                        c0 = b0
                        root = roots[1] # get next root
                        if root==0: # check for root = 0
                            st.write(f'Another rational root is 0. So we can just divide the equation by x:')
                            b2 = c3
                            b1 = c2
                            b0 = c1
                            st.write('We now have a quadratic equation:')
                            st.latex(f'{b2}x^2 + {b1}x + {b0} = 0.')
                            chk3 = True # set flag that we are ready to solve the quadratic

                        elif (root%1 == 0): # whole number root
                            root = int(root)
                            st.write(f'Another rational root is: {root}')
                            st.write('Use synthetic division to reduce this cubic equation to a quadratic:')
                            sdiv_df = pd.DataFrame({
                                '0': [f'{root} __|', '', '', ''],
                                '  ' : [c3, '', '---', '[  ]'],
                                '   ' : [c2, '', '---', '[  ]'],
                                '    ' : [c1, '', '---', '[  ]'],
                                '     ' : [c0, '', '---', ''],
                            })
                            sdiv_df.set_index('0',inplace=True)
                            st.table(sdiv_df)
                            b2 = c3
                            b1 = b2*root + c2
                            b0 = b1*root + c1
                            chk3 = False
                            b2_in = st.text_input(' 1st blank ', value = '')
                            b1_in = st.text_input(' 2nd blank ', value = '')
                            b0_in = st.text_input(' 3rd blank ', value = '')
                            if (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                                b2_in = int(b2_in)
                                b1_in = int(b1_in)
                                b0_in = int(b0_in)
                                if (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                    st.write('Try again.')
                                    chk3 = False
                                else:
                                    st.write('Nicely done! We now have a quadratic equation:')
                                    st.latex(f'{b2}x^2 + {b1}x + {b0} = 0.')
                                    chk3 = True # set flag that we are ready to solve the quadratic
                        elif (root%1!=0): #fraction root
                            if root>0:
                                numer, denom = decimal_to_fraction(root)
                                st.write(f'Another rational root is {root}, or {numer}/{denom}.')
                            else:
                                numer, denom = decimal_to_fraction(-1*root)
                                st.write(f'Another rational root is {root}, or -{numer}/{denom}.')
                               
                            st.write('Even though this is a fraction, we can still use synthetic division to reduce this cubic equation to a quadratic;')
                            st.write(f' we just have to divide by {denom} at the end.')
                            sdiv_df = pd.DataFrame({
                                '0': [f'{root} __|', '', '', ''],
                                '  ' : [c3, '', '---', '[  ]'],
                                '   ' : [c2, '', '---', '[  ]'],
                                '    ' : [c1, '', '---', '[  ]'],
                                '     ' : [c0, '', '---', ''],
                            })
                            sdiv_df.set_index('0',inplace=True)
                            st.table(sdiv_df)
                            b2 = c3
                            b1 = b2*root + c2
                            b0 = b1*root + c1
                            chk3 = False
                            b2_in = st.text_input(' 1st blank ', value = '')
                            b1_in = st.text_input(' 2nd blank ', value = '')
                            b0_in = st.text_input(' 3rd blank ', value = '')
                            if (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                                b2_in = int(b2_in)
                                b1_in = int(b1_in)
                                b0_in = int(b0_in)
                                if (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                    st.write('Try again.')
                                    chk3 = False
                                else:
                                    b2 = int(b2/denom)
                                    b1 = int(b1/denom)
                                    b0 = int(b0/denom)
                                    st.write(f'Nicely done! After dividing those all by {denom}, we have a quadratic equation:')
                                    st.latex(f'{b2}x^2 + {b1}x + {b0} = 0.')
                                    chk3 = True # set flag that we are ready to solve the quadratic

            else: # start with cubic
                chk5 = True
                if chk5==True:
                    chk4 = True
                    if chk4==True:
                        c3 = b3
                        c2 = b2
                        c1 = b1
                        c0 = b0
                        root = roots[0]
                        if root==0: # check for root = 0
                            st.write(f'One rational root is 0. So we can just divide the equation by x:')
                            b2 = c3
                            b1 = c2
                            b0 = c1
                            st.write('We now have a quadratic equation:')
                            st.latex(f'{b2}x^2 + {b1}x + {b0} = 0.')
                            chk3 = True # set flag that we are ready to solve the quadratic

                        elif (root%1 == 0): # whole number root 
                            root = int(root)
                            st.write(f'One rational root is: {root}')
                            st.write('Use synthetic division to reduce this cubic equation to a quadratic:')
                            sdiv_df = pd.DataFrame({
                                '0': [f'{root} __|', '', '', ''],
                                '  ' : [c3, '', '---', '[  ]'],
                                '   ' : [c2, '', '---', '[  ]'],
                                '    ' : [c1, '', '---', '[  ]'],
                                '     ' : [c0, '', '---', ''],
                            })
                            sdiv_df.set_index('0',inplace=True)
                            st.table(sdiv_df)
                            b2 = c3
                            b1 = b2*root + c2
                            b0 = b1*root + c1
                            chk3 = False
                            b2_in = st.text_input(' 1st blank ', value = '')
                            b1_in = st.text_input(' 2nd blank ', value = '')
                            b0_in = st.text_input(' 3rd blank ', value = '')
                            if (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                                b2_in = int(b2_in)
                                b1_in = int(b1_in)
                                b0_in = int(b0_in)
                                if (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                    st.write('Try again.')
                                    chk3 = False
                                else:
                                    st.write('Nicely done! We now have a quadratic equation:')
                                    st.latex(f'{b2}x^2 + {b1}x + {b0} = 0.')
                                    chk3 = True # set flag that we are ready to solve the quadratic
                        elif (root%1!=0): # fraction root
                            numer, denom = decimal_to_fraction(root)
                            st.write(f'One rational root is {root}, or {numer}/{denom}.')
                            st.write('Even though this is a fraction, we can still use synthetic division to reduce this cubic equation to a quadratic;')
                            st.write(f' we just have to divide by {denom} at the end.')
                            sdiv_df = pd.DataFrame({
                                '0': [f'{root} __|', '', '', ''],
                                '  ' : [c3, '', '---', '[  ]'],
                                '   ' : [c2, '', '---', '[  ]'],
                                '    ' : [c1, '', '---', '[  ]'],
                                '     ' : [c0, '', '---', ''],
                            })
                            sdiv_df.set_index('0',inplace=True)
                            st.table(sdiv_df)
                            b2 = c3
                            b1 = b2*root + c2
                            b0 = b1*root + c1
                            chk3 = False
                            b2_in = st.text_input(' 1st blank ', value= '')
                            b1_in = st.text_input(' 2nd blank ', value= '')
                            b0_in = st.text_input(' 3rd blank ', value= '')
                            if (b2_in.isnumeric) and (b1_in.isnumeric) and (b0_in.isnumeric):
                                b2_in = int(b2_in)
                                b1_in = int(b1_in)
                                b0_in = int(b0_in)
                                if (b2_in!=b2) or (b1_in!=b1) or (b0_in!=b0):
                                    st.write('Try again.')
                                    chk3 = False
                                else:
                                    b2 = int(b2/denom)
                                    b1 = int(b1/denom)
                                    b0 = int(b0/denom)
                                    st.write(f'Nicely done! After dividing those all by {denom}, we have a quadratic equation:')
                                    st.latex(f'{b2}x^2 + {b1}x + {b0} = 0.')
                                    chk3 = True # set flag that we are ready to solve the quadratic

            if chk3==True: # solve the quadratic
                st.write('Almost done! Solve the quadratic by the method of your choice (square roots, factoring, completing the square, quadratic formula)')
                st.write('Select all CORRECT solutions below.')

                # under the hood -- solve by quadratic formula. User can use whichever method they like
                negb = -1*b1
                twoa = 2*b2
                disc = b1*b1 - 4*b2*b0
                vertex_x = negb/twoa
                if vertex_x == 0:
                    vert_str = ''
                elif vertex_x%1 == 0:
                    vert_str = f'{vertex_x}'
                elif vertex_x > 0:
                    numer, denom = decimal_to_fraction(vertex_x)
                    vert_str = f'{numer}/{denom}'
                elif vertex_x < 0:
                    numer, denom = decimal_to_fraction(-1*vertex_x)
                    vert_str = f'-{numer}/{denom}'
                if disc==0: # discriminant = 0, only 1 real solution
                    sqrt_str = ''
                    wrong = f'{b0}'
                    correct = [vert_str]
                    solution_options = [vert_str, wrong]
                    solution_options.sort()
                    sel1 = st.checkbox(solution_options[0])
                    sel2 = st.checkbox(solution_options[1])
                    if   (sel1==True) and (solution_options[0] not in correct): st.write('Try again.')
                    elif (sel2==True) and (solution_options[1] not in correct): st.write('Try again.')
                    elif (sel1!=True) and (solution_options[0] in correct): st.write('Try again.')
                    elif (sel2!=True) and (solution_options[1] in correct): st.write('Try again.')
                    else:
                        st.write('You did it!')
                        st.balloons()
                else: # 2 solutions
                    if disc>0: #2 real solutions
                        out_rad, in_rad, denom = simplify_radical(disc/(twoa*twoa))
                    else: # 2 complex solutions
                        out_rad, in_rad, denom = simplify_radical(-1*disc/(twoa*twoa))
                    if out_rad==1: # format for whether there is a square root, a fraction, i
                        if in_rad==1:
                            if denom==1:
                                str1 = '1'
                                str2 = 'i'
                            else:
                                str1 = f'1 / {denom}'
                                str2 = f'i / {denom}'
                        else:
                            if denom==1:
                                str1 = f'square_root( {in_rad} )'
                                str2 = f'i square_root( {in_rad} )'
                            else:
                                str1 = f'square_root( {in_rad} ) / {denom}'
                                str2 = f'i square_root( {in_rad} ) / {denom}'
                    else:
                        if in_rad==1:
                            if denom==1:
                                str1 = f'{out_rad}'
                                str2 = f'{out_rad}i'
                            else:
                                str1 = f'{out_rad} / {denom}'
                                str2 = f'{out_rad}i / {denom}'
                        else:
                            if denom==1:
                                str1 = f'{out_rad} square_root( {in_rad} )'
                                str2 = f'{out_rad}i square_root( {in_rad} )'
                            else:
                                str1 = f'{out_rad} square_root( {in_rad} ) / {denom}'
                                str2 = f'{out_rad}i square_root( {in_rad} ) / {denom}'
                    if disc>0: # solutions are real (no "i")
                        sqrt_str = str1
                        wrong = str2
                    else: # solutions are complex ("i")
                        sqrt_str = str2
                        wrong = str1
                    if vertex_x == 0: # correct formating if b=0
                        correct = [sqrt_str, '-' + sqrt_str]
                    else: # or b not = 0
                        correct = [vert_str + ' + ' + sqrt_str, vert_str + ' - ' + sqrt_str]
                    correct = [c if ('square_root' in c) or ('i' in c) else str(np.round(eval(c),4)) for c in correct] # get decimals where appropriate
                    incorrect = [vert_str + ' + ' + wrong, vert_str + ' - ' + wrong]
                    incorrect = [c if ('square_root' in c) or ('i' in c) else str(np.round(eval(c),4)) for c in incorrect]
                    solution_options = correct + incorrect
                    solution_options.sort()
                    sel1 = st.checkbox(solution_options[0])
                    sel2 = st.checkbox(solution_options[1])
                    sel3 = st.checkbox(solution_options[2])
                    sel4 = st.checkbox(solution_options[3])
                    if   (sel1==True) and (solution_options[0] not in correct): st.write('Try again.')
                    elif (sel2==True) and (solution_options[1] not in correct): st.write('Try again.')
                    elif (sel3==True) and (solution_options[2] not in correct): st.write('Try again.')
                    elif (sel4==True) and (solution_options[3] not in correct): st.write('Try again.')
                    elif (sel1!=True) and (solution_options[0] in correct): st.write('Try again.')
                    elif (sel2!=True) and (solution_options[1] in correct): st.write('Try again.')
                    elif (sel3!=True) and (solution_options[2] in correct): st.write('Try again.')
                    elif (sel4!=True) and (solution_options[3] in correct): st.write('Try again.')
                    else:
                        st.write('You did it!')
                        st.balloons()
