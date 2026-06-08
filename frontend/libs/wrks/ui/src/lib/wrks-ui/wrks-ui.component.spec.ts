import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksUiComponent } from './wrks-ui.component';

describe('WrksUiComponent', () => {
  let component: WrksUiComponent;
  let fixture: ComponentFixture<WrksUiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksUiComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksUiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
