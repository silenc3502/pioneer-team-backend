from dataclasses import dataclass


CONTENT_KEY_MAX_LENGTH = 255


@dataclass(frozen=True)
class ContentFilter:
    prefix: str | None = None

    def __post_init__(self) -> None:
        if self.prefix is None:
            return
        if not self.prefix:
            raise ValueError("콘텐츠 키는 빈 문자열일 수 없습니다.")
        if len(self.prefix) > CONTENT_KEY_MAX_LENGTH:
            raise ValueError(
                f"콘텐츠 키 길이는 {CONTENT_KEY_MAX_LENGTH}자를 초과할 수 없습니다."
            )

    @property
    def is_active(self) -> bool:
        return self.prefix is not None
