# GDBAI
GDB AI assistant plugin. Debug with GPT.

GDB AI助手插件,和GPT一起debug.

# Usage

## set your openai api key,proxy, language
设置你的openai api key

(可选)设置你的代理,回答语言
```
export OPENAI_API_KEY="your key"
# [optional]
export http_proxy=http://username:password@proxy_host:proxy_port
export https_proxy=http://username:password@proxy_host:proxy_port
export GDBAI_LANG=zh
export GDBAI_MODEL="gpt-3.5-turbo"
```

## example

## command
- ai - Answer questions based on current stack information
- chat - Chat with GPT
- trans - Translate natural language into a GDB command
- explain - Explain the meaning of a GDB command
## 命令
- ai - 根据当前堆栈信息回答问题
- chat - 和GPT聊天
- trans - 将自然语言翻译称一条GDB命令
- explain - 解释GDB命令的含义

## load
`(gdb) source /path/to/gdbai/gdbai.py ` every time or add it to `.gdbinit`

```
(gdb) source /path/to/gdbai/gdbai.py 
usage:
        ai
        ai Explain what the root cause of this error is.Give me Suggestions
        ai 用中文回答无效指针是哪个
        chat how to use gdb
        trans show the instructions at the current location
        explain handle SIGINT stop
(gdb) r
Starting program: /path/to/gdbai/debug_demo 
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".

Program received signal SIGSEGV, Segmentation fault.
0x0000555555555236 in print (p=0x0) at debug_demo.cpp:9
warning: Source file is more recent than executable.
9         std::cout<< *p << std::endl;
(gdb) ai 
Based on the provided GDB debug information, the error seems to occur in the "print" function at line 9 of the "debug_demo.cpp" file. The error is caused by accessing a null pointer (p=0x0).

The root cause of this error is that the "print" function is receiving a null pointer (p) as an argument. Trying to access the memory location pointed to by a null pointer will result in a segmentation fault or other similar error.

To resolve this issue, you should ensure that the pointer being passed to the "print" function is not null before attempting to access its value. You can add a null check at the beginning of the function to handle such cases gracefully:

void print(int* p) {
    if (p == nullptr) {
        // Handle the case when p is null
        std::cout << "Error: Null pointer passed to print function\n";
        return;
    }

    // Rest of your code to print the value pointed by p
    // ...
}

By adding this null check, you can avoid the segmentation fault and handle the null pointer case in a more controlled manner.
(gdb) ai 用中文回答无效指针是哪个,是谁调用这个函数的
根据给出的GDB调试信息，我们可以看到位于print函数中的NULL指针。

当前函数是print函数，它在debug_demo.cpp文件的第9行被调用。
调用print函数的是main函数，它位于debug_demo.cpp文件的第15行。

希望这能帮到你！
(gdb) trans show the instructions at the current location
x/8i $pc

=> 0x555555555236 <_Z5printPi+20>:      mov    (%rax),%eax
   0x555555555238 <_Z5printPi+22>:      mov    %eax,%esi
   0x55555555523a <_Z5printPi+24>:      lea    0x2dff(%rip),%rdi        # 0x555555558040 <_ZSt4cout@GLIBCXX_3.4>
   0x555555555241 <_Z5printPi+31>:      call   0x5555555550d0 <_ZNSolsEi@plt>
   0x555555555246 <_Z5printPi+36>:      mov    %rax,%rdx
   0x555555555249 <_Z5printPi+39>:      mov    0x2d80(%rip),%rax        # 0x555555557fd0
   0x555555555250 <_Z5printPi+46>:      mov    %rax,%rsi
   0x555555555253 <_Z5printPi+49>:      mov    %rdx,%rdi
(gdb) explain x/8i $pc
The GDB command "x/8i $pc" is used to display the next 8 instructions of the program being debugged starting from the current value of the program counter ($pc).

The "x" command is used in GDB to examine memory. In this case, we are using it to examine the instructions in memory. The "8i" argument specifies that we want to examine 8 instructions, and the "$pc" specifies that we want to start examining from the current value of the program counter.

The program counter ($pc) keeps track of the memory address of the next instruction to be executed by the processor. By using the "x/8i" command with the $pc register, we can see the assembly instructions that are about to be executed.

The output of this command will show the memory addresses and corresponding assembly instructions for the next 8 instructions in the program. This can be useful for understanding program flow and debugging issues at the instruction level.
(gdb) chat what's gdb
GDB (GNU Debugger) is a powerful and widely used debugger for various programming languages, including C, C++, and assembly. It allows developers to trace and debug their programs by providing features such as breakpoints, stepping through code, examining variables and memory, and controlling program execution. GDB is a command-line tool that is commonly used in development environments for finding and fixing software bugs and errors.
```
# ToDo
Welcome to raise an issue. If there are more stars, it will speed up development.
- [ ] The information provided to AI includes source code, balancing token length limitations and the issue of necessary information.
- [ ] Add task decomposition for debugging, automate calling functions to obtain the required additional information to complete debugging.

欢迎提issue,如果星星多的话,会加快开发
- [ ] 提供给AI的信息包含source code,平衡token长度限制和必要信息的问题
- [ ] 增加debug任务拆解,自动化调用函数获取需要的补充信息完成debug