# Persistent-Variables
Simple persistent variables in python (not to be confused with pointers)

## Basic Example
```python
import pvars
pvars = pvars.get_context()

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
pvars = pvars.get_context()

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
### Module
Returns a ModuleContext object configured according to any options passed to it. The object can then be used to create p vars. It can also be seen as the database object itself.
```python
get_context(extra_path = "", abs_path = "", **config_params)
```


### ModuleContext class
Creates a new p var
```python
make_var(default, lambda_func)
```
The function should almost _always_ be used like in this example
```python
global var
var = make_var(None, lambda: var)
```

Configures the object. The extra kwargs passed to `get_context` are passed here
```python
configure(*, auto_save: bool = None, file_format: pvars.Format = None, **dump_args)
```

Resets all variables
```python
reset()
```

Returns all existing variables as a dict
```python
all()
```

Saves all existing variables
```python
save()
```

## Implementation details and complications
The data itself is stored in a file... WIP The format used is by default pickle, but can also be configured to JSON or CSV. Keep in mind the restrictions these formats impose. Keep the default format (Pickle), to be the least restricted.

## Okayyy, but I got (insert generic DB), why would I want this?
This library represent a shift in how you view persisent data. Instead of seeing it in the light of whatever database is used, it's represented as what it truly is, with lower level details abstracted away. It's also a great libary for beginners, since fewer choices and actions are necessary than usually. These aspects result in less and clearer code. Another interesting detail is that every db is by default created per module/script and not per main script, offering library developers a cleaner and more standardized alternative to config files.  
