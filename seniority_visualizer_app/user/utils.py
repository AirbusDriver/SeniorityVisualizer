from enum import IntFlag


class BaseTwoAutoEnum(IntFlag):
    """
    Enumeration providing programmatic access to bitwise Enumeration members.

    ..usage::

        >>> from enum import unique, auto
        >>> class MyBitwiseEnum(BaseTwoAutoEnum):
        ...     A = auto()
        ...     B = auto()
        ...     C = auto()
        >>> MyBitwiseEnum.A
        <MyBitwiseEnum.A>
        >>> print(MyBitwiseEnum.A)
        MyBitwiseEnum.A
        >>> print(MyBitwiseEnum.C.bit_mask)
        100
        >>> (MyBitwiseEnum.A | MyBitwiseEnum.B) == 3
        True
        >>> (MyBitwiseEnum.A | MyBitwiseEnum.B) == 1
        False
        >>> top_dog = sum(MyBitwiseEnum)  # has all permissions
        >>> something = (MyBitwiseEnum.A | MyBitwiseEnum.B)  # some perm requirement
        >>> something & top_dog == something
        True
        >>> middle_dog = MyBitwiseEnum.A | MyBitwiseEnum.C  # top_dogs only!!!
        >>> top_dog & middle_dog == top_dog
        False
        >>> top_dog & top_dog == top_dog  # but a top_dog can do it
        True
    """

    def _generate_next_value_(name, start, count, last_values):
        """
        Return a bit mask that identifies each Enum member as unique
        """
        return 1 << count

    @property
    def bit_mask(self):
        """Return a string representation of the bitmask of the member"""
        return bin(self)[2:].zfill(len(type(self)))

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"
