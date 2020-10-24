# Persistent-Variables
Simple persistent variables in python (not to be confused with pointers)

## Basic Example
```python
import pvars
pvars = pvars.get_context(auto_save=True)

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
    pvars.save()
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

## Another Example 
Sometimes you need to edit the p vars directly. A pydb database can be "reduced" to a persistent dict behaving much like the one in the `shelve` module. In the dict, each key is a variable.
```python
import pvars
first_db = pvars.get_context(abs_path = "path/to/db1.pydb").all()
for key in first_db.keys():
    first_db[key] += 1
first_db.sync() # Doesn't need to (and can't) be closed, only synced
```
Take care when mixing direct editing with indirect editing, the code wasn't written with this usage in mind

## Last example
It's also possible to create a sort of hybrid between a shelve and pvar, a so called `idict`
```python
import pvars
pvars = pvars.get_context()
def main():
    a = pvars.make_dict({"Hello": 5}, "IndexA")
    b = a
    b["Hello"] += 1
```
### First run
```python
{"Hello": 5}
```
### Second run
```python
{"Hello": 6}
```
`auto_save` was off, and we didn't call `save`, so how could our changes be stored? Because the `idict` automatically saves when assigned to. idicts and pvars can seamlessly be combined.


## API Documentation
### Module
Returns a ModuleContext object configured according to any options passed to it. The object can then be used to create pvars. It can also be seen as the database object itself, with the internal database being accessible through the `all()` member
```python
import pvars
pvars = pvars.get_context()
```


### ModuleContext class
Creates a new p var
```python
make_var(default, lambda_func)
```
The function should usually be used like this:
```python
global var
var = make_var(None, lambda: var)
```

Creates a new idict. Make sure to use a unique name each time this function is called, and don't lose track of your idicts.
```python
make_dict(default, name)
```

Configures the object. The extra kwargs passed to `get_context` are passed here
```python
configure(*, auto_save: bool = False, file_format: pvars.Format = None, **dump_args)
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

### Idict class
Indentical to `ModuleContext.save()`
```python
save()
```

## Implementation details and complications
The data itself is stored in a file with the .pdb extension and with the same name as the module. The format used is by default pickle, but can also be configured to JSON or CSV. Keep in mind the restrictions these formats impose. Keep the default format (Pickle), to be the least restricted. There are 3 ways to make sure data is saved.
- Call the `save()` function before exiting
- Assign to an `idict` before exiting
- Enable auto-save

Autosave will attempt to save when python exits. "Attempt" as in, having registered with the `atexit` module and also listening `ctrl-c` to events. This has worked fine for me, but I can't promise anything, so it's also an option to disable auto save and save manually whenever appropriate.

## Okayyy, but I got (insert generic DB), why would I want this?
This library represent a shift in how you view persisent data. Instead of seeing it in the light of whatever database is used, it's represented as what it truly is, with lower level details abstracted away. It's also a great libary for beginners, since fewer choices and actions are necessary than usually. These aspects result in less and clearer code. Another interesting detail is that every db is by default created per module/script and not per main script, offering library developers a cleaner and more standardized alternative to config files.

The downsides are obviously that everything is loaded into memory and that the data can only really be accessed conveniently by a single module. So speed, flexibility, control and reliability are sacrificed.
