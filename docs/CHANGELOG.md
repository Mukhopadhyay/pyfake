---
icon: lucide/calendar-days
tags:
  - Get started
  - Setup
hide:
  - title
---

# Changelog 🕓

### `0.0.14` - 2026-11-17

A bug-fix release. Models that used to crash or fail validation now generate valid data, and many more pydantic types are supported.

**Bug fixes**

* **One-sided bounds**: `Field(ge=500)`, `Field(le=-5)` or `Field(ge=date(2200, 1, 1))` no longer crash with `empty range`. When a single bound falls outside the default range, the range keeps its default width and moves next to that bound. This applies to `int`, `float`, `Decimal`, `date`, `datetime` and `timedelta`.
* **`time` bounds at second 59**: `Field(gt=time(12, 0, 59))` no longer raises `second must be in 0..59`.
* **Constrained types**: `conint`, `constr`, `confloat`, `condecimal`, `conlist`, `conset`, `annotated_types.Interval`, `StringConstraints` and bare `annotated_types` constraints (`Annotated[int, Gt(0)]`) are now respected, including inside containers such as `List[conint(gt=0)]`.
* **Aliases**: fields with an `alias` or `validation_alias` now validate. Models are built with `model_validate(data, by_name=True)`.
* **Self-referencing models**: models such as `class Node(BaseModel): children: List["Node"]` no longer raise `RecursionError`. Generation stops adding nested items once a model appears 3 times on a path. A self-reference that can never be empty (a required `child: "Node"`) raises `InvalidConstraints`. Forward references to models defined later in the module are resolved, as pydantic does on first use.
* **`min_length=0`** is honoured, so lists, sets, tuples and dicts can be empty. A `min_length` above 5 with no `max_length` no longer crashes.
* **Sets, frozensets and dict keys** always reach `min_length`. Values are generated until they are distinct, and an impossible request such as `Set[bool]` with `min_length=3` raises `InvalidConstraints`.
* **Reproducible UUIDs**: every UUID version now draws from the seeded random stream, so `fake(Model, seed=1) == fake(Model, seed=1)` holds for UUID fields too. Time-based versions (v1, v6, v7) use a timestamp from the 24 hours before the start of the current UTC day.
* **Relative and timezone types**: `PastDate`, `FutureDate`, `PastDatetime`, `FutureDatetime`, `AwareDatetime` and `NaiveDatetime` are supported, and no longer fail validation at random.
* **Unsupported types**: instead of silently returning `None` (which then failed validation), pyfake raises `GeneratorNotFound` with the field path, e.g. `No generator registered for type <class 'pathlib.Path'> (field 'User.avatar')`.
* **Regex `pattern`** is now enforced. Strings are generated from the parsed pattern and checked against it.
* **Callable `json_schema_extra`**: `Field(json_schema_extra=lambda schema: ...)` no longer raises `AttributeError`.
* **Decimals**: an unbounded `Decimal` now has 2 decimal places instead of ~50 digits of float noise, and `max_digits` is honoured.
* **Floats**: exclusive bounds (`gt`, `lt`) are now exact, so narrow ranges such as `gt=0, lt=0.05` stay valid.
* **Timeseries**: the `shift` anomaly no longer raises `TypeError`, and several shifts now stack. The `seasonal_anomaly` type is implemented (it was a silent no-op). Seeding no longer changes NumPy's global random state.
* **Warnings**: no more `PydanticSerializationUnexpectedValue` warnings for date and time bounds.
* **`fake.seed(42)`** now returns a reproducible *stream*: each call returns a new row, and the whole sequence is the same every run. Before, every call returned the same row. A per-call `seed=` still returns the same rows on every call.
* **`num=0`** returns `[]` instead of one row. A negative `num` raises `ValueError`.

**New supported types**

* `EmailStr`, `NameEmail`
* `AnyUrl`, `HttpUrl`, `FileUrl`, `FtpUrl`, `WebsocketUrl` and every DSN type (`PostgresDsn`, `RedisDsn`, `MongoDsn`, ...). URLs use the schemes the type allows, on `example.*` hosts.
* `IPv4Address`, `IPv6Address`, `IPv4Network`, `IPv6Network`, `IPv4Interface`, `IPv6Interface` and pydantic's `IPvAny*` types
* `SecretStr`, `SecretBytes`, `bytes`, `ByteSize` (and other subclasses of supported types)
* `timedelta`, `Any`, `object`, `None`
* `FrozenSet`, `Sequence`, `MutableSequence`, `Iterable`, `deque`, `Mapping`, `MutableMapping`, `OrderedDict`, `DefaultDict`, `Counter`, `AbstractSet`, and bare `list` / `dict` / `tuple` / `set`
* `json_schema_extra={"format": ...}` accepts JSON Schema format names (`"email"`, `"uri"`, `"ipv4"`, `"duration"`, ...) to pick a generator for a `str` field.

**Behaviour changes**

* Seeded output differs from `0.0.13` for UUIDs, `Decimal`s, floats with `gt`/`lt`, sets, fields with `min_length=0`, and timeseries noise, anomalies and missing values.
* `Fake(seed=...)` and `fake.seed(...)` keep one random stream across calls (see above).
* Unsupported field types raise `GeneratorNotFound` instead of returning `None`.
* `InvalidConstraints` is now also a `ValueError`.
* Generated models are built with `model_validate`, so a custom `__init__` on your model is not called.
* `Timeseries` raises `ValueError` for an unknown anomaly `type`.

**Docs**

* Brought every page in line with the current behaviour: container length rules, `Decimal` defaults, regex support, seeding, the types returned in dicts (`UUID`, tuples, sets, enum members), and the error raised for unsupported types.
* New page: [Other types](https://mukhopadhyay.is-a.dev/pyfake/pydantic/special-types/) (emails, URLs, IP addresses, secrets, bytes, `timedelta`, constrained types, abstract containers).
* Rewrote the timeseries guide and added [Advanced features](https://mukhopadhyay.is-a.dev/pyfake/timeseries/advanced-features/) (noise, seasonality, anomalies, missing values, value constraints).
* Fixed the Python version badge (3.10+), the requirements list, and links to the documentation site.

**Testing**

* 470 -> 1,242 tests; coverage 91% -> 99% (timeseries 61% -> 100%).

### `0.0.13` - 2026-06-27

**New Features**

* **Timezone-aware datetimes**: Pass any datetime.`tzinfo` subclass — including `datetime.timezone` constants and `zoneinfo.ZoneInfo` instances — through `json_schema_extra={"timezone": ...}` on a datetime field. Supporting attributes such as,

```python
class Event(BaseModel):
    # stdlib UTC constant
    utc_ts: Annotated[
        datetime, Field(..., json_schema_extra={"timezone": timezone.utc})
    ]
    # IANA timezone via zoneinfo
    ny_ts: Annotated[
        datetime,
        Field(..., json_schema_extra={"timezone": ZoneInfo("America/New_York")}),
    ]
```

### `0.0.12` - 2026-06-23

**Major changes**

* Feature, allowing users to create more realistic and complex time series data. The implementation is designed to be extensible for future enhancements. (`pyfake/core/timeseries.py`)

* Implemented support for `noise`, `seasonality`, `anomalies`, `missing values`, and value `constraints` in the **`Timeseries`** class. The class now includes methods to inject these features into generated data, and the constructor accepts new parameters for each

**Docs**

* Added detailed documentation for the new timeseries features, including explanations of noise, seasonality, anomalies, missing values, and constraints, along with code examples and usage guidelines. ([advanced features](timeseries/advanced-features.md))
* Replaced mermaid chart with a static image for better presentation




### `0.0.11` - 2026-06-21

**Major changes**

* Added a new **Timeseries** class to pyfake.core.timeseries, supporting generation of time series data with configurable start, periods, frequency, baseline, trend (`upward`, `downward`, `flat`), and reproducibility via seed. The implementation is extensible for future features like noise, seasonality, anomalies, and missing data, but currently implements only baseline and linear trend. (`pyfake/core/timeseries.py`)

* The project now depends on [`Numpy`](https://numpy.org/) for internal calculations, and the documentation has been updated to reflect this change. The installation verification instructions have been removed from the docs since Numpy is now a required dependency. (`docs/index.md`)

**Docs**

* Added a comprehensive **"Getting Started"** guide for the new timeseries feature, including API usage, code examples, limitations, and tips for reproducibility. (`docs/timeseries/getting-started.md`)
* Updated the main documentation to clarify that Numpy is now a requirement and removed outdated installation verification instructions. (`docs/index.md`)
* Added a reference to the **"how it works"** section for further reading. (`docs/index.md`)

---

### `0.0.10` - 2026-04-19

**Minor changes**

* **Packaging and type hinting**: Added a `py.typed` marker to the package data for pyfake in pyproject.toml, indicating that the package includes type hints for static type checkers.

---

### `0.0.9` - 2026-04-09

**New Features**
-  Support for `multiple_of` constraint for numeric fields, allowing users to specify that generated numbers must be multiples of a given value. This is implemented in the generator registry and integrated into the schema resolution process.
- Improved support for the `decimal_places` option for both `float` and `Decimal` fields, with documentation clarifying floating-point precision nuances.

**Docs**
- Added comprehensive new documentation pages for datetime and uuid usage, including examples, option explanations, and implementation notes.
- Updated the README with a clearer quick example, a new feature matrix comparing pyfake to other generators, and a more concise project introduction.

---

### `0.0.8` - 2026-04-06

**Major changes**

- Introduced the Fake class as a new, user-friendly API for generating fake data (`from pyfake import fake`), accessible via the fake singleton in `pyfake/__init__.py`. This class provides methods for generating data as dicts, models, or JSON, and supports seeding for reproducibility. (`pyfake/core/api.py`, `pyfake/__init__.py`)
  
**New Features**

- Added support for the `Decimal` type, including generator registration and type mapping in the registry.
- Improved metadata parsing for field constraints (e.g., `pattern`, `decimal_places`) and fixed a bug in how these are extracted from Pydantic field metadata.

**Docs**
- Added comprehensive usage guides for [booleans](https://mukhopadhyay.is-a.dev/pyfake/pydantic/boolean/), [numbers](https://mukhopadhyay.is-a.dev/pyfake/pydantic/numbers/) (including constraints and Decimal), and [strings](https://mukhopadhyay.is-a.dev/pyfake/pydantic/strings/), with examples and notes on supported/unsupported features.
- Updated the main [README.md](https://github.com/Mukhopadhyay/pyfake/blob/master/README.md) with new documentation links and fixed minor formatting issues.

---

### `0.0.7` - 2026-04-02

**Major changes**

- Recursive generator support for nested Pydantic models
- Recursive resolver for resolving nested Pydantic models in the input Schema


**New Features**

- Support for `datetime`, `date` & `time` formats
  - Ability to set bounds using pydantic [`Field()`](https://docs.pydantic.dev/latest/concepts/fields/) function
- Flag based return for either accepting a **dictionary** or the **input Pydantic model** (`as_dict = True`)
- Updated ReadTheDocs documentation
- Support for `list`, `set` and `tuple` types with length constraints using pydantic [`Field()`](https://docs.pydantic.dev/latest/concepts/fields/) function
- Moving documentations to [`zensical`](https://zensical.org/) for better experience and future support.

---

### `0.0.6` - 2026-01-30

**Major changes**

- Migrated the entire project to [`uv`](https://docs.astral.sh/uv/) for faster, deterministic dependency management and installs.
- Introduced a new modular and expandable architecture, separating concerns into:
  - `engine` – execution and orchestration layer
  - `registry` – type to generator resolution
  - `context` – shared runtime state and randomness control

**New Features**

- Added full support for UUID generation across all formats:
  - `UUID1`, `UUID3`, `UUID4`, `UUID5`, `UUID6`, `UUID7`, `UUID8`
- Added support for legacy primitive types:
  - `int`
  - `float`
  - `str`
- Introduced a reproducible generation context, allowing users to set a seed for deterministic fake data generation.

**Testing**

- Added **comprehensive test coverage** across all generators and core components.
- Tests now validate:
  - Correct type resolution
  - Deterministic output with seeded contexts
  - UUID format correctness
  - Edge cases across primitive and complex generators

---

### `0.0.5` - 2025-06-16

- Initial release
