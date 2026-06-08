import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommUiComponent } from './comm-ui.component';

describe('CommUiComponent', () => {
  let component: CommUiComponent;
  let fixture: ComponentFixture<CommUiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommUiComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommUiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
