import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstUiComponent } from './asst-ui.component';

describe('AsstUiComponent', () => {
  let component: AsstUiComponent;
  let fixture: ComponentFixture<AsstUiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstUiComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstUiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
