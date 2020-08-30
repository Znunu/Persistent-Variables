# Persistent-Variables
Simple persistent variables in python (not to be confused with pointers)

## Basic Example
```python
import pvars

if __name__ == '__main__':
    main()
 
def main():
    global a
    a = pvars.make_var(123, lambda: a)
    print(a)
    a = 999
    print(a)
```
### First run
```python
123
999
```
### Second run
```python
999
999
```

## Advanced Example
```python
import pvars

if __name__ == '__main__':
    main()
 
def main():
    global open_count
    open_count = pvars.make_var(0, lambda: open_count)
    open_count += 1
    print(open_count)
    global var
    var = pvars.make_var("hello", lambda: var)
    print(var)
    if not isinstance(var, dict): var = {}
    var[f"key{open_count}"] = "hello"
    print(var)
```
### First run
```python
1
hello
{'key1': 'hello'}
```
### Second run
```python
2
{'key1': 'hello'}
{'key1': 'hello', 'key2': 'hello'}
```

## API Documentation
Create a new persistent variable
```
make_var(default, lambda)
```
The function should _always_ be used like this
```
global var
var = make_var(default, lambda: var)
```

Resets all variables
```
reset()
```

Returns all existing variables as a dict
```
all()
```

Saves all existing variables
```
save()
```

Configures the modules
```
configure(*, auto_save: bool = None, file_format: pvars.Format = None, extra_param: dict = None)
```

## Implementation details and complications
The data itself is stored in a file with the same name as the main script but with the ".pdb" extensions instead. The format used is by default pickle, but can also be configured to JSON or CSV. Keep in mind the restrictions these formats impose. Keep the default format (Pickle), to be the least restricted.
